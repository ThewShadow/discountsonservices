from django.urls import path, include
from . import views

app_name = 'service'

urlpatterns = [
    path('accounts/login/',
         views.Login.as_view(),
         name='login'),

    path('accounts/register/',
         views.Registration.as_view(),
         name='registration'),

    path('accounts/verify_email/',
         views.VerifyEmail.as_view(),
         name='verify_email'),

    path('accounts/reset_password/start/',
         views.ResetPassword.as_view(),
         name='reset_pass'),

    path('accounts/reset_password/confirm/',
         views.ResetPasswordConfirm.as_view(),
         name='reset_pass_confirm'),

    path('accounts/reset_password/complete/',
         views.ResetPasswordComplete.as_view(),
         name='reset_pass_complete'),

    path('social/google_oauth2/login_complete/',
         views.GoogleLoginComplete.as_view(),
         name='google-auth2-complete'),

    path('social/google_oauth2/login/',
         views.GoogleLogin.as_view(),
         name='google-auth2'),

    path('payments/crypto/create/',
         views.CryptoPayCreate.as_view(),
         name='cryptogen'),

    path('subscriptions/create/',
         views.SubscriptionCreate.as_view(),
         name='create_subscription'),

    path('payments/paypal/create/',
         views.PayPalCreate.as_view(),
         name='paypal_form_create'),

]