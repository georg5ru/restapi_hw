from django.urls import path
from users.views import (
    PaymentListAPIView, UserProfileAPIView, UserRegistrationView,
    PaymentCreateView, PaymentStatusView, PaymentSuccessView, PaymentCancelView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:payment_id>/status/', PaymentStatusView.as_view(), name='payment-status'),
    path('payments/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payments/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('users/<int:pk>/', UserProfileAPIView.as_view(), name='user-profile'),
]