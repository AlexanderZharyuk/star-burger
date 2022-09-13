import requests

from django import forms
from django.shortcuts import redirect, render
from django.conf import settings
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from distances.models import Place


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in
                        product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for
                                restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.summary() \
        .filter(status__in=['NP', 'IP', 'ID']) \
        .prefetch_related('products__product') \
        .prefetch_related('restaurant') \
        .order_by('-status')
    menu_items = RestaurantMenuItem.objects.all() \
        .select_related('product').select_related('restaurant') \
        .exclude(availability=False)
    places = {place.address: {
        'lat': place.latitude,
        'lon': place.longitude
    } for place in Place.objects.all()}

    for order in orders:
        order.restaurants = {}
        order.valid_address = True
        order.available_restaurants = set()

        for position_in_order, item in enumerate(order.products.all()):
            available_restaurants = [
                restaurant_item.restaurant for restaurant_item in menu_items
                if item.product.id == restaurant_item.product.id
            ]
            if not order.available_restaurants and not position_in_order:
                order.available_restaurants = set(available_restaurants)
                continue

            order.available_restaurants &= set(available_restaurants)

        for restaurant in order.available_restaurants:
            if restaurant.address not in places.keys():
                restaurant_coordinates = _get_address_coordinates(restaurant.address)
            else:
                restaurant_coordinates = places[restaurant.address]['lat'], \
                                         places[restaurant.address]['lon']
            if order.address not in places.keys():
                order_coordinates = _get_address_coordinates(order.address)
            else:
                order_coordinates = places[order.address]['lat'], \
                                    places[order.address]['lon']

            if not order_coordinates:
                order.valid_address = False
                break

            order.restaurants[restaurant] = round(
                distance.distance(restaurant_coordinates, order_coordinates)
                .km, 2)
        order.restaurants = \
            dict(sorted(order.restaurants.items(), key=lambda item: item[1]))

    context = {
        'order_items': orders,
    }
    return render(request, template_name='order_items.html',
                  context=context)


def _fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def _get_address_coordinates(address):
    place, created = Place.objects.get_or_create(address=address)

    if not created:
        return place.latitude, place.longitude

    place_coordinates = _fetch_coordinates(settings.YANDEX_API_KEY, address)
    if not place_coordinates:
        return False

    place.address = address
    place.latitude, place.longitude = place_coordinates
    place.save()
    return place.latitude, place.longitude
