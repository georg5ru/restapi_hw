from rest_framework import serializers
from users.models import User, Payment
from materials.serializers import CourseSerializer, LessonSerializer
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации новых пользователей
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'phone', 'city', 'avatar')
        extra_kwargs = {
            'phone': {'required': False},
            'city': {'required': False},
            'avatar': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя с историей платежей
    """
    payments = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'full_name', 'payments']
        read_only_fields = ['id', 'email']

    def get_payments(self, obj):
        """Возвращает платежи пользователя"""
        payments = obj.payments.all()
        return PaymentSerializer(payments, many=True).data

    def get_full_name(self, obj):
        """Возвращает полное имя пользователя"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для платежей с детальной информацией
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    paid_course_detail = CourseSerializer(source='paid_course', read_only=True)
    paid_lesson_detail = LessonSerializer(source='paid_lesson', read_only=True)
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'payment_date',
            'amount',
            'payment_method',
            'payment_method_display',
            'payment_status',
            'payment_status_display',
            'paid_course',
            'paid_course_detail',
            'paid_lesson',
            'paid_lesson_detail',
            'stripe_payment_url',
        ]
        read_only_fields = ['payment_date', 'payment_status']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания платежа через Stripe
    """

    class Meta:
        model = Payment
        fields = ['paid_course', 'paid_lesson', 'amount']

    def validate(self, data):
        """Проверяем, что указан хотя бы один объект для оплаты"""
        if not data.get('paid_course') and not data.get('paid_lesson'):
            raise serializers.ValidationError(
                "Необходимо указать курс или урок для оплаты"
            )
        if data.get('paid_course') and data.get('paid_lesson'):
            raise serializers.ValidationError(
                "Нельзя одновременно оплачивать курс и урок"
            )

        # Проверяем, что сумма положительная
        if data.get('amount', 0) <= 0:
            raise serializers.ValidationError(
                "Сумма должна быть больше 0"
            )

        return data


class PaymentStatusSerializer(serializers.Serializer):
    """
    Сериализатор для проверки статуса платежа
    """
    payment_id = serializers.IntegerField(help_text="ID платежа в системе")