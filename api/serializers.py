from rest_framework import serializers
from .models import Category, Dish, Order, OrderItem
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    dishes = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'dishes', 'status', 'created_at', 'user']
        extra_kwargs = {
            'user': {'read_only': True},
            'status': {'read_only': False},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        dishes_data = validated_data.pop('dishes')
        order = Order.objects.create(**validated_data)
        for dish_data in dishes_data:
            OrderItem.objects.create(
                order=order,
                dish=dish_data['dish'],
                quantity=dish_data['quantity']
            )
        return order

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_admin'] = user.is_staff
        token['is_waiter'] = user.is_waiter
        token['is_kitchen'] = user.is_kitchen
        return token
