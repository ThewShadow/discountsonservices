from django.urls import path, include
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView
from django.contrib.auth.views import PasswordResetCompleteView
from django_registration.forms import RegistrationFormUniqueEmail
from django_registration.views import RegistrationView
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/subscriptions/', views.UserSubscriptionsView.as_view(), name='user_subscriptions'),

    path('accounts/password_reset/', PasswordResetView.as_view(
        template_name='main/password_reset_form.html'),
        name='password_reset'),

    path('accounts/reset/done/', PasswordResetCompleteView.as_view(
        template_name='main/password_reset_done.html'),
        name='password_reset_complete'),

    path('accounts/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='main/password_reset_confirm.html'),
        name='password_reset_confirm'),

    path('accounts/password_reset/done/', PasswordResetDoneView.as_view(
        template_name='main/password_reset_complete.html'),
        name='password_reset_done'),

    path('social/', include('social_django.urls', namespace='social')),

    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/register/', RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name='django_registration_register'),

    path('accounts/', include('django_registration.backends.one_step.urls')),

    path('offers/<slug:slug>/<slug:rate_slug>/', views.OffersView.as_view(), name='offers'),
    path('offers/<slug:slug>/', views.OffersView.as_view() , name='offers_redirect'),

    path('subscription/<int:offer_id>', views.SubscriptionCreateView.as_view() ,name='subscribe'),
    path('not_authorizate/', views.NotAuthorizate.as_view(), name='not_authorizate'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),

    path('faq/', views.FAQView.as_view(), name='faq_list'),
    path('admin_panel/', views.ManagerPanelView.as_view(), name='manager_panel'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment_paypal/', views.PaypalFormView.as_view(), name='paypal_order_create'),
    path('paypal_return/', views.PayPalPaymentReturnView.as_view(), name='paypal_return'),
    path('paypal_cancel/', views.PayPalPaymentCancelView.as_view(), name='paypal_cancel'),

]
