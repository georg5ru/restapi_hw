import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    """Фильтр для платежей"""

    # Фильтрация по курсу
    course = django_filters.NumberFilter(field_name='course', lookup_expr='exact')

    # Фильтрация по уроку
    lesson = django_filters.NumberFilter(field_name='lesson', lookup_expr='exact')

    # Фильтрация по способу оплаты
    payment_method = django_filters.ChoiceFilter(
        field_name='payment_method',
        choices=[('cash', 'Наличные'), ('bank_transfer', 'Перевод на счет')]
    )

    # Сортировка по дате
    ordering = django_filters.OrderingFilter(
        fields=(
            ('payment_date', 'payment_date'),
        ),
        field_labels={
            'payment_date': 'Дата оплаты',
        }
    )

    class Meta:
        model = Payment
        fields = ['course', 'lesson', 'payment_method']