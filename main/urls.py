from django.urls import path, include
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView
from django.contrib.auth.views import PasswordResetCompleteView
from django_registration.forms import RegistrationFormUniqueEmail
from django_registration.views import RegistrationView
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('profile/info', views.ProfileView.as_view(), name='profile'),
    path('profile/subscriptions/', views.UserSubscriptionsView.as_view(), name='user_subscriptions'),

    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', views.RegistrationView.as_view(), name='registration'),
    path('accounts/verify_email/', views.VerifyEmailView.as_view(), name='verify_email'),

    path('accounts/reset_password/start/', views.ResetPasswordView.as_view(), name='reset_pass'),
    path('accounts/reset_password/confirm/', views.ResetPasswordConfirmView.as_view(), name='reset_pass_confirm'),
    path('accounts/reset_password/complete/', views.ResetPasswordCompleteView.as_view(), name='reset_pass_complete'),

    path('accounts/social/login_complete/', views.GoogleLoginCompleteView.as_view(), name='google-auth2-complete'),
    path('accounts/social/login/', views.GoogleLoginView.as_view(), name='google-auth2'),

    path('offers/<slug:slug>/<slug:rate_slug>/', views.OffersView.as_view(), name='offers'),
    path('offers/<slug:slug>/', views.OffersView.as_view() , name='offers_redirect'),

    #path('subscription/<int:offer_id>', views.SubscriptionCreateView.as_view() ,name='subscribe'),
    path('not_authorizate/', views.NotAuthorizate.as_view(), name='not_authorizate'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),

    path('faq/', views.FAQView.as_view(), name='faq_list'),
    path('admin_panel/', views.ManagerPanelView.as_view(), name='manager_panel'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('paypal_return/', views.PaidCompleteView.as_view(), name='paypal_return'),
    path('paypal_cancel/', views.PayPalPaymentCancelView.as_view(), name='paypal_cancel'),


]
