from django.urls import path, include
from main import views

urlpatterns = [# api methods
    path('subscriptions/create/', views.SubscriptionCreateView.as_view(), name='create_subscription'),
    path('payments/paypal/create/', views.PayPalFormView.as_view(), name='paypal_form_create'),
]