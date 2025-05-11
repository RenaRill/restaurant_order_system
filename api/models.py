from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class Category(models.Model):
    name = models.CharField(max_length=100)


class Dish(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Order(models.Model):
    STATUS_CHOICES = [
        ('ACCEPTED', 'Принят'),
        ('DELIVERED', 'Подан'),
        ('PAID', 'Оплачен')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dishes = models.ManyToManyField(Dish, through='OrderItem')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACCEPTED')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class User(AbstractUser):
    is_waiter = models.BooleanField(default=False)
    is_kitchen = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='api_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='api_user_permissions',
        blank=True
    )
