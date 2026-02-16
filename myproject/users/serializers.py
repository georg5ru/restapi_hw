from rest_framework import serializers
from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'course', 'course_title', 'lesson', 'lesson_title',
            'amount', 'payment_method'
        ]
        read_only_fields = ['user']


class UserSerializer(serializers.ModelSerializer):
    """Расширенный сериализатор пользователя с историей платежей"""

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'city', 'avatar', 'payments'
        ]