# Generated by Django 3.2.15 on 2022-09-16 11:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_alter_itemsinorder_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemsinorder',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='foodcartapp.product', verbose_name='Товар'),
        ),
    ]
