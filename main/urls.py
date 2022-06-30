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

    path('accounts/logout/', views.LogoutView.as_view(), name='logout'),

    path('offers/<slug:slug>/<slug:rate_slug>/', views.OffersView.as_view(), name='offers'),
    path('offers/<slug:slug>/', views.OffersView.as_view() , name='offers_redirect'),

    path('not_authorizate/', views.NotAuthorizate.as_view(), name='not_authorizate'),
    path('support/', views.SupportView.as_view(), name='support'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),

    path('faq/', views.FAQView.as_view(), name='faq_list'),
    path('admin_panel/', views.ManagerPanelView.as_view(), name='manager_panel'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('paypal_return/', views.PaidCompleteView.as_view(), name='paypal_return'),
    path('paypal_cancel/', views.PayPalPaymentCancelView.as_view(), name='paypal_cancel'),



]
