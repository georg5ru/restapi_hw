from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import Payment, User
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    PaymentSerializer,
    CustomTokenObtainPairSerializer
)
from .filters import PaymentFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': 'Пользователь успешно зарегистрирован'
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Разные права для разных действий"""
        if self.action == 'create':
            # Регистрация доступна всем
            permission_classes = [AllowAny]
        else:
            # Остальные действия требуют авторизации
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Пользователь видит только себя или все (если админ)"""
        user = self.request.user

        # Если не суперпользователь, возвращаем только себя
        if not user.is_superuser:
            return User.objects.filter(id=user.id)

        return super().get_queryset()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный view для получения токена"""
    serializer_class = CustomTokenObtainPairSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежей с фильтрацией"""
    queryset = Payment.objects.select_related('user', 'course', 'lesson').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def perform_create(self, serializer):
        """Автоматически привязываем платеж к текущему пользователю"""
        serializer.save(user=self.request.user)