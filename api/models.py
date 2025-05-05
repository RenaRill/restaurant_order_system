from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)


class Dish(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('PREP', 'Готовится'),
        ('DONE', 'Завершен'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Кто создал заказ
    dishes = models.ManyToManyField(Dish, through='OrderItem')
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
