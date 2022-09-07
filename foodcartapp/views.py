from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction
from rest_framework.serializers import ValidationError, ModelSerializer, ListField
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, ItemsInOrder


class OrderSerializer(ModelSerializer):
    products = ListField(
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname',
                  'phonenumber', 'address']

    def validate_products(self, user_request):
        max_product_id = Product.objects.all().count()
        for product in user_request:
            product_id = product['product']
            if product_id > max_product_id:
                raise ValidationError(
                    f'products: Недопустимый первичный ключ {product_id}'
                )
        return user_request


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


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    order = request.data
    serializer = OrderSerializer(data=order)
    serializer.is_valid(raise_exception=True)

    founded_order, created = Order.objects.get_or_create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address']
    )

    products_in_order = serializer.validated_data['products']
    for product in products_in_order:
        product_id = product['product']
        product_quantity = product['quantity']

        founded_product = Product.objects.get(id=product_id)
        ItemsInOrder.objects.create(
            order=founded_order,
            product=founded_product,
            item_quantity=product_quantity,
            price=founded_product.price
        )

    order_id = Order.objects.all().count()
    server_response = {'id': order_id}
    server_response.update(serializer.data)
    return Response(server_response)
