import pytest
from django.utils import timezone
from datetime import timedelta
from users.models import Subscription


@pytest.mark.django_db
class TestSubscriptionModel:
    def test_subscription_creation(self, user):
        """Тест создания подписки"""
        subscription = Subscription.objects.create(
            user=user,
            end_date=timezone.now() + timedelta(days=30)
        )
        assert subscription.user == user
        assert subscription.is_active is True

    def test_subscription_is_valid(self, user):
        """Тест проверки активности подписки"""
        subscription = Subscription.objects.create(
            user=user,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30)
        )
        assert subscription.is_valid() is True

    def test_subscription_expired(self, user):
        """Тест истекшей подписки"""
        subscription = Subscription.objects.create(
            user=user,
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=30)
        )
        assert subscription.is_valid() is False