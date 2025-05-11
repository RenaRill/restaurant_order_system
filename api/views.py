from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from .models import Category, Dish, Order
from .serializers import CategorySerializer, DishSerializer, OrderSerializer, CustomTokenObtainPairSerializer
from .permissions import IsAdmin, IsWaiter, ReadOnly, IsKitchen
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin | ReadOnly]


class DishViewSet(ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [IsAdmin | ReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin | IsWaiter | IsKitchen]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_permissions(self):
        # Только официанты могут создавать заказы
        if self.action == 'create':
            return [IsWaiter()]
        return [perm() for perm in self.permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()

        if IsKitchen().has_permission(self.request, self):
            # Кухня видит только заказы со статусом ACCEPTED
            return queryset.filter(status='ACCEPTED')

        if IsWaiter().has_permission(self.request, self):
            # Официант видит только свои заказы
            queryset = queryset.filter(user=self.request.user)

        # Фильтр по статусу
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    def perform_create(self, serializer):
        # Указание официанта при создании заказа
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Официант может редактировать только свой заказ
        if IsWaiter().has_permission(request, self) and order.user != request.user:
            return Response({'detail': 'Вы можете редактировать только свои заказы.'}, status=status.HTTP_403_FORBIDDEN)

        # Кухне нельзя редактировать заказ
        if IsKitchen().has_permission(request, self):
            return Response({'detail': 'Кухне запрещено изменять заказы.'}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()

        # Кухня может видеть только заказы со статусом ACCEPTED
        if IsKitchen().has_permission(request, self) and order.status != 'ACCEPTED':
            return Response({'detail': 'Кухне разрешён доступ только к заказам со статусом ACCEPTED.'},
                            status=status.HTTP_403_FORBIDDEN)

        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsWaiter])
    def mark_delivered(self, request, pk=None):
        # Официант отмечает подачу блюда
        order = self.get_object()
        if order.user != request.user:
            return Response({'detail': 'Можно изменить только свои заказы.'}, status=status.HTTP_403_FORBIDDEN)
        order.status = 'DELIVERED'
        order.save()
        return Response({'status': 'delivered'})

    @action(detail=True, methods=['post'], permission_classes=[IsWaiter])
    def mark_paid(self, request, pk=None):
        # Официант отмечает оплату
        order = self.get_object()
        if order.user != request.user:
            return Response({'detail': 'Можно изменить только свои заказы.'}, status=status.HTTP_403_FORBIDDEN)
        order.status = 'PAID'
        order.save()
        return Response({'status': 'paid'})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
