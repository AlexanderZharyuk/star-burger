import json

from django.http import JsonResponse
from django.templatetags.static import static


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


def register_order(request):
    try:
        order = json.loads(request.body.decode())
    except ValueError:
        return JsonResponse({})

    products_in_order = order['products']
    founded_order, created = Order.objects.get_or_create(
        name=order['firstname'],
        surname=order['lastname'],
        phone_number=order['phonenumber'],
        address=order['address']
    )

    for product in products_in_order:
        product_id = product['product']
        product_quantity = product['quantity']

        founded_product = Product.objects.get(id=product_id)
        ItemsInOrder.objects.create(
            order=founded_order,
            product=founded_product,
            item_quantity=product_quantity
        )

    return JsonResponse(order)
