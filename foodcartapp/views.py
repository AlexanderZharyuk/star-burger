from textwrap import dedent

import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, ItemsInOrder


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order = request.data
    form_errors = _get_errors_from_order_form(order)
    if form_errors:
        return Response(form_errors, status.HTTP_400_BAD_REQUEST)

    founded_order, created = Order.objects.get_or_create(
        name=order['firstname'],
        surname=order['lastname'],
        phone_number=order['phonenumber'],
        address=order['address']
    )

    products_in_order = order['products']
    for product in products_in_order:
        product_id = product['product']
        product_quantity = product['quantity']

        founded_product = Product.objects.get(id=product_id)
        ItemsInOrder.objects.create(
            order=founded_order,
            product=founded_product,
            item_quantity=product_quantity
        )
    return Response(order)


def _get_errors_from_order_form(order):
    required_fields = ['products', 'firstname', 'lastname',
                       'phonenumber', 'address']
    not_passed_required_fields = [field for field in required_fields if not
                                  order.get(field)]
    if not_passed_required_fields:
        fields = ', '.join(not_passed_required_fields)
        error_detail = '''You didn't pass all required field(s).'''
        response = {
            'description': dedent(error_detail).replace('\n', ' '),
            'missed_field(s)': fields,
            'notice': 'Required fields can\'t be empty'
        }
        return response

    products_in_order = order['products']
    if not isinstance(products_in_order, list):
        parameter_type = type(products_in_order).__name__
        error_detail = f'''\
        Required field 'products' must be list type,
        got {parameter_type} type.'''
        response = {'description': dedent(error_detail).replace('\n', ' ')}
        return response

    fields_that_must_be_string = [
        'firstname', 'lastname', 'phonenumber', 'address'
    ]
    fields_with_incorrect_type = [
        field for field in fields_that_must_be_string if not
        isinstance(order[field], str)
    ]
    for field in fields_with_incorrect_type:
        field_type = type(order[field]).__name__
        error_detail = f'''\
        Required field '{field}' must be string type, got {field_type} type.'''
        response = {'description': dedent(error_detail)}
        return response

    max_product_id = Product.objects.all().count()
    for product in products_in_order:
        if product['product'] > max_product_id:
            error_detail = '''Required field 'product' is not valid.'''
            response = {'description': error_detail}
            return response

    user_phone_number = order['phonenumber']
    parsed_phone_number = phonenumbers.parse(user_phone_number)
    if not phonenumbers.is_valid_number(parsed_phone_number):
        error_detail = '''Phone number is not valid'''
        response = {'description': error_detail}
        return response
