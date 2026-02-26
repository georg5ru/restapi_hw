from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Менеджер для модели User, где email используется для аутентификации."""

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт обычного пользователя."""
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт суперпользователя."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Наследуемся от AbstractUser, но меняем поле для авторизации на email.
    """
    username = None  # убираем поле username
    email = models.EmailField(unique=True, verbose_name='Email')

    # Добавляем новые поля
    phone = models.CharField(max_length=35, verbose_name='Телефон', blank=True, null=True)
    city = models.CharField(max_length=50, verbose_name='Город', blank=True, null=True)
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар', blank=True, null=True)

    # Указываем, что поле email будет использоваться для входа
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # обязательные поля при createsuperuser (кроме email)

    objects = CustomUserManager()  # подключаем кастомный менеджер

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель платежа с поддержкой Stripe"""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод на счет'
        STRIPE = 'stripe', 'Stripe'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        PAID = 'paid', 'Оплачен'
        FAILED = 'failed', 'Ошибка'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='пользователь'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата оплаты'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        verbose_name='способ оплаты'
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name='статус оплаты'
    )

    # Оплаченный курс или урок (используем строки для избежания циклических импортов)
    paid_course = models.ForeignKey(
        'materials.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='оплаченный курс'
    )
    paid_lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='оплаченный урок'
    )

    # Поля для Stripe
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID продукта в Stripe'
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID цены в Stripe'
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID сессии в Stripe'
    )
    stripe_payment_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на оплату в Stripe'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.user.email} - {self.amount} руб. ({self.get_payment_method_display()})"