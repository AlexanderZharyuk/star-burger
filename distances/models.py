from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(
        max_length=120,
        verbose_name='Адрес',
        unique=True
    )
    latitude = models.DecimalField(
        'Широта',
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        'Долгота',
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        blank=True,
        null=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Последнее время обновления',
        default=timezone.now
    )

    def __str__(self):
        return f'{self.address}: {self.updated_at}'
