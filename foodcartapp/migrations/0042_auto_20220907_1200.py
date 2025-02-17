# Generated by Django 3.2.15 on 2022-09-07 11:14

from django.db import migrations


def set_orders_price(apps, schema_editor):
    ItemsInOrder = apps.get_model('foodcartapp', 'ItemsInOrder')
    items = ItemsInOrder.objects.all().iterator()

    for item in items:
        item.price = item.quantity * item.product.price
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_itemsinorder_price'),
    ]

    operations = [
        migrations.RunPython(set_orders_price),
    ]
