# Generated by Django 3.2.15 on 2022-09-16 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_alter_order_restaurant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itemsinorder',
            old_name='item_quantity',
            new_name='quantity',
        ),
    ]
