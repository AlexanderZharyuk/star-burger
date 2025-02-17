# Generated by Django 3.2.15 on 2022-09-16 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0056_alter_itemsinorder_order'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='restaurant',
            new_name='cooking_restaurant',
        ),
        migrations.AlterField(
            model_name='order',
            name='paid_status',
            field=models.CharField(choices=[('CASH', 'Наличными'), ('CARD', 'Интернет-эквайринг'), ('NOT_CHOSEN', 'Не выбран')], default='NOT_CHOSEN', max_length=50, verbose_name='Способ оплаты'),
        ),
    ]
