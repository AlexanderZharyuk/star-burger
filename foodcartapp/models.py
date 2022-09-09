from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def summary(self):
        amount_order = self.annotate(
            amount=Sum(
                F('products__item_quantity') * F('products__product__price'))
        )
        return amount_order


class Order(models.Model):
    NOT_PROCESSED = 'NP'
    IN_PROCESS = 'IP'
    IN_DELIVERY = 'ID'
    PROCESSED = 'OP'
    PAID_BY_CASH = 'CASH'
    PAID_BY_CARD = 'CARD'

    ORDER_STATUS_CHOICES = [
        (NOT_PROCESSED, 'Не обработан'),
        (IN_PROCESS, 'Собирается рестораном'),
        (IN_DELIVERY, 'В доставке'),
        (PROCESSED, 'Обработан')
    ]
    ORDER_PAID_STATUS_CHOICES = [
        (PAID_BY_CASH, 'Наличными'),
        (PAID_BY_CARD, 'Интернет-эквайринг')
    ]

    status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS_CHOICES,
        default=NOT_PROCESSED,
        verbose_name='Статус заказа',
        db_index=True
    )
    paid_status = models.CharField(
        max_length=50,
        verbose_name='Способ оплаты',
        choices=ORDER_PAID_STATUS_CHOICES,
        default=PAID_BY_CASH
    )
    restaurant = models.ForeignKey(
        'Restaurant',
        on_delete=models.CASCADE,
        verbose_name='Ресторан, который приготовит заказ',
        related_name='orders',
        null=True
    )
    firstname = models.CharField(
        'Имя',
        max_length=25
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=25
    )
    phonenumber = PhoneNumberField(
        'Номер телефона'
    )
    address = models.CharField(
        'Адрес',
        max_length=100
    )
    comment = models.TextField(
        'Комментарий',
        blank=True
    )
    registered_at = models.DateTimeField(
        'Дата регистрации заказа',
        default=timezone.now,
        blank=True
    )
    called_at = models.DateTimeField(
        'Дата звонка менеджера',
        blank=True,
        null=True
    )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        blank=True,
        null=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname}, {self.address}"


class ItemsInOrder(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='products',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        related_name='order',
        on_delete=models.CASCADE
    )
    item_quantity = models.IntegerField(
        verbose_name='Количество'
    )
    price = models.DecimalField(
        'Цена позиции',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True
    )

    def __str__(self):
        return f'Продукт {self.product.name} в количестве {self.item_quantity}'
