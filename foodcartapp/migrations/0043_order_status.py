# Generated by Django 3.2.15 on 2022-09-07 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20220907_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Нет', 'Не обработан'), ('Да', 'Обработан')], default='Нет', max_length=12, verbose_name='Статус заказа'),
        ),
    ]
