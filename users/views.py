from rest_framework import generics, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.urls import reverse
import django_filters

from users.models import Payment, User
from users.serializers import (
    PaymentSerializer, UserSerializer, UserRegistrationSerializer,
    PaymentCreateSerializer, PaymentStatusSerializer
)
from users.services import (
    create_stripe_product, create_stripe_price,
    create_stripe_checkout_session, retrieve_stripe_session
)


class PaymentFilter(django_filters.FilterSet):
    """Кастомный фильтр для платежей"""

    class Meta:
        model = Payment
        fields = {
            'paid_course': ['exact', 'isnull'],
            'paid_lesson': ['exact', 'isnull'],
            'payment_method': ['exact'],
            'payment_status': ['exact'],
            'amount': ['exact', 'gte', 'lte'],
        }


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей - только для авторизованных"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']

    def get_queryset(self):
        # Пользователи видят только свои платежи
        return self.queryset.filter(user=self.request.user)


class PaymentCreateView(APIView):
    """
    Создание платежа через Stripe
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        amount = float(data.get('amount', 0))
        paid_course = data.get('paid_course')
        paid_lesson = data.get('paid_lesson')

        # Определяем название продукта
        if paid_course:
            product_name = f"Курс: {paid_course.title}"
            product_description = paid_course.description[:100]
        else:
            product_name = f"Урок: {paid_lesson.title}"
            product_description = paid_lesson.description[:100]

        # Создаем продукт в Stripe
        product_id = create_stripe_product(product_name, product_description)
        if not product_id:
            return Response(
                {"error": "Ошибка создания продукта в Stripe"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Создаем цену в Stripe
        price_id = create_stripe_price(amount, product_id)
        if not price_id:
            return Response(
                {"error": "Ошибка создания цены в Stripe"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Создаем сессию для оплаты
        success_url = request.build_absolute_uri(reverse('payment-success'))
        cancel_url = request.build_absolute_uri(reverse('payment-cancel'))

        session_data = create_stripe_checkout_session(price_id, success_url, cancel_url)
        if not session_data:
            return Response(
                {"error": "Ошибка создания сессии оплаты"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Сохраняем платеж в базе
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            payment_method=Payment.PaymentMethod.STRIPE,
            payment_status=Payment.PaymentStatus.PENDING,
            paid_course=paid_course,
            paid_lesson=paid_lesson,
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            stripe_session_id=session_data['id'],
            stripe_payment_url=session_data['url'],
        )

        # Возвращаем ссылку на оплату
        return Response({
            'payment_id': payment.id,
            'payment_url': session_data['url'],
            'message': 'Платеж создан, перейдите по ссылке для оплаты'
        }, status=status.HTTP_201_CREATED)


class PaymentStatusView(APIView):
    """
    Проверка статуса платежа
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        # Если платеж уже оплачен, возвращаем статус
        if payment.payment_status == Payment.PaymentStatus.PAID:
            return Response({
                'payment_id': payment.id,
                'status': payment.payment_status,
                'message': 'Платеж уже оплачен'
            })

        # Проверяем статус в Stripe
        if payment.stripe_session_id:
            session_data = retrieve_stripe_session(payment.stripe_session_id)
            if session_data:
                if session_data['payment_status'] == 'paid':
                    payment.payment_status = Payment.PaymentStatus.PAID
                    payment.save()

        return Response({
            'payment_id': payment.id,
            'status': payment.payment_status,
            'stripe_status': session_data['payment_status'] if session_data else None
        })


class PaymentSuccessView(APIView):
    """
    Страница успешной оплаты
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'message': 'Оплата прошла успешно!',
            'status': 'success'
        })


class PaymentCancelView(APIView):
    """
    Страница отмены оплаты
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'message': 'Оплата отменена',
            'status': 'cancelled'
        })


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя - доступно всем"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileAPIView(generics.RetrieveAPIView):
    """Просмотр профиля пользователя - только авторизованные"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]