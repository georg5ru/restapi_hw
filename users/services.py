import stripe
from django.conf import settings
from typing import Dict, Any, Optional

# Инициализация Stripe с секретным ключом
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name: str, description: str = "") -> Optional[str]:
    """
    Создание продукта в Stripe

    Args:
        name: Название продукта
        description: Описание продукта

    Returns:
        ID созданного продукта или None в случае ошибки
    """
    try:
        product = stripe.Product.create(
            name=name,
            description=description
        )
        return product.id
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None


def create_stripe_price(amount: float, product_id: str) -> Optional[str]:
    """
    Создание цены для продукта в Stripe

    Args:
        amount: Сумма в рублях
        product_id: ID продукта в Stripe

    Returns:
        ID созданной цены или None в случае ошибки
    """
    try:
        # Stripe принимает сумму в копейках
        price = stripe.Price.create(
            unit_amount=int(amount * 100),
            currency="rub",
            product=product_id,
        )
        return price.id
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None


def create_stripe_checkout_session(price_id: str, success_url: str, cancel_url: str) -> Optional[Dict[str, Any]]:
    """
    Создание сессии для оплаты в Stripe

    Args:
        price_id: ID цены в Stripe
        success_url: URL для перенаправления после успешной оплаты
        cancel_url: URL для перенаправления после отмены оплаты

    Returns:
        Объект сессии Stripe или None в случае ошибки
    """
    try:
        session = stripe.checkout.Session.create(
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="payment",
        )
        return {
            'id': session.id,
            'url': session.url,
            'payment_status': session.payment_status,
        }
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None


def retrieve_stripe_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Получение информации о сессии оплаты

    Args:
        session_id: ID сессии в Stripe

    Returns:
        Объект сессии Stripe или None в случае ошибки
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'id': session.id,
            'payment_status': session.payment_status,
            'customer_email': session.customer_details.email if session.customer_details else None,
        }
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None