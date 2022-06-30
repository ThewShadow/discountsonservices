from django.shortcuts import redirect, get_object_or_404, render, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView, FormView, CreateView, TemplateView, View, RedirectView
from datetime import datetime
from . import service
from social_django.models import UserSocialAuth
from django.core.exceptions import PermissionDenied
from paypal.standard.forms import PayPalPaymentsForm
from django.utils.translation import get_language
from config import settings
from .models import CustomUser
from .models import Offer
from .models import Subscription
from .models import Product
from .models import FAQ
from .forms import RegistrationForm
from .forms import LoginForm
from .forms import SupportCreateTaskForm
from .forms import ChangeUserInfoForm
from .forms import ChangeSubscibeStatusForm
from .forms import SubscribeCreateForm
from .forms import VerifyEmailForm
from .forms import CustomUserCreationForm
from .forms import ResetPasswordForm
from .forms import ResetPasswordVerifyForm
from .forms import NewPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class CommonMixin:

    def get_common_data(self, request, **kwargs):
        kwargs['all_products'] = Product.objects.all()
        kwargs['login_form'] = LoginForm()
        kwargs['register_form'] = RegistrationForm()
        kwargs['verify_email_form'] = VerifyEmailForm()
        kwargs['questions_list'] = FAQ.objects.all()
        kwargs['forget_pass_code_form'] = ResetPasswordVerifyForm()
        kwargs['forget_pass_email_form'] = ResetPasswordForm()
        kwargs['new_pass_form'] = NewPasswordForm()

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        common = self.get_common_data(self.request, **kwargs)
        return dict(list(context.items()) + list(common.items()))


class PaidCompleteView(View):

    def get(self, request, **kwargs):
        response = redirect('index')
        response.set_cookie(key='paid_success', value=True)
        return response


class IndexView(CommonMixin, ListView):
    template_name = 'main/index.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        logger.info('ss')

        return context


class LogoutView(View):

    def post(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse_lazy('index'))

    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse_lazy('index'))


class OffersView(CommonMixin, ListView):
    template_name = 'main/offers.html'
    model = Offer

    def get(self, *args, **kwargs):
        rate_slug = self.kwargs.get('rate_slug', None)
        if not rate_slug:
            product_slug = self.kwargs.get('slug', None)
            offers = Offer.objects.filter(product__slug=product_slug)


            if offers.exists():
                min_offer = offers.order_by('price')
                min_offer = min_offer.first()
                rate_slug = min_offer.rate.slug

            if rate_slug:
                kwargs['slug'] = product_slug
                kwargs['rate_slug'] = rate_slug
                return redirect(reverse_lazy('offers', kwargs=kwargs))

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        form = SubscribeCreateForm(self.request.POST)
        if form.is_valid():
            new_subscription = Subscription.objects.create(form)
            new_subscription.save()

            resp = {'sub_id': new_subscription.id}
            return HttpResponse(resp, status=200)
        else:
            return HttpResponse({'error': True}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('slug')
        context['product'] = get_object_or_404(Product, slug=product_id)
        context['sub_create_form'] = SubscribeCreateForm()

        rate_slug = self.kwargs.get('rate_slug', None)
        if rate_slug:
            context['rate_slug'] = rate_slug
            context['offers'] = Offer.objects.filter(product__slug=product_id,
                                                     rate__slug=rate_slug).order_by('price')
            rates = []
            for offer in Offer.objects.filter(product__slug=product_id).order_by('price'):
                if offer.rate not in rates:
                    rates.append(offer.rate)

            context['rates'] = rates
        else:
            context['offers'] = Offer.objects.filter(product__slug=product_id)

        return context


class ProfileView(CommonMixin, LoginRequiredMixin, FormView):
    template_name = 'main/user_profile.html'
    login_url = 'not_authorizate'
    redirect_field_name = 'redirect_to'
    form_class = ChangeUserInfoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user_inst = self.request.user
        initial_data = {'username': user_inst.username, 'email': user_inst.email}
        context['object'] = get_object_or_404(CustomUser, id=self.request.user.id)
        context['form'] = ChangeUserInfoForm(initial=initial_data)
        context['questions_list'] = FAQ.objects.all()
        return context

    def post(self, *args, **kwargs):
        form = ChangeUserInfoForm(self.request.POST)
        if form.is_valid():
            change_profile_info(self.request, form)

        return super().post(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('profile')


class NotAuthorizate(CommonMixin, TemplateView):
    template_name = 'main/not_authorizate.html'


class SupportView(CommonMixin, LoginRequiredMixin, CreateView):
    template_name = 'main/support.html'
    model = User
    form_class = SupportCreateTaskForm
    login_url = 'not_authorizate'
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy('index')

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        initial['pub_date'] = datetime.now()
        return initial

    def form_valid(self, form):
        task_instance = form.save(commit=True)
        service.send_support_task(task_instance.id)
        return redirect(reverse_lazy('index'))


class AboutUsView(CommonMixin, TemplateView):
    template_name = 'main/about_us.html'


class UserSubscriptionsView(CommonMixin, LoginRequiredMixin, ListView):
    login_url = 'not_authorizate'
    redirect_field_name = 'redirect_to'
    model = Subscription
    form_class = ChangeUserInfoForm
    template_name = 'main/user_subscriptions.html'

    def get_context_data(self, *args, **kwargs):
        context= super().get_context_data()
        context['user_subscriptions'] = Subscription.objects.filter(
            user__id=self.request.user.id)
        return context


class ManagerPanelView(CommonMixin, LoginRequiredMixin, TemplateView):
    template_name = 'main/manager_panel.html'

    def get(self, request, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied()

        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        form = ChangeSubscibeStatusForm(request.POST)
        if form.is_valid():
            subscr_obj = get_object_or_404(Subscription, id=form.cleaned_data['sub_id'])
            subscr_obj.status = form.cleaned_data['status_value']
            subscr_obj.is_active = True
            subscr_obj.save()
            subscr_obj.notify_customer()

        return redirect(reverse_lazy('manager_panel'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_subscriptions'] = Subscription.objects.filter(status=1).order_by('-order_date')
        context['all_statuses'] = Subscription.STATUSES
        return context


class FAQView(CommonMixin, ListView):
    model = FAQ
    template_name = 'main/faq.html'
    context_object_name = 'questions_list'


class PayPalPaymentCancelView(CommonMixin, TemplateView):
    template_name = 'payments/paypal_cancel.html'


class PayPalPaymentReturnView(CommonMixin, TemplateView):
    template_name = 'payments/paypal_return.html'

    def get(self, request, **kwargs):
        response = super().get(request, **kwargs)
        response.set_cookie(key='paid_success', value=True)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.request.session.get('sub_id', None)
        return context


def user_email_uniq(user, email):
    return CustomUser.objects.exclude(id=user.id).filter(email=email).count() == 0 \
           and UserSocialAuth.objects.exclude(user=user).filter(uid=email).count() == 0

def change_profile_info(request, form):
    user = request.user
    new_username = form.cleaned_data.get('username')
    new_email = form.cleaned_data.get('email')

    if user.email == new_email and user.username == new_username:
        return

    from django.contrib import messages

    if user_email_uniq(user, new_email):
        user.email = new_email
        user.username = new_username
        try:
            social_user = UserSocialAuth.objects.get(user__id=request.user.id)
        except:
            pass
        else:
            social_user.uid = new_email
            social_user.save()
        finally:
            user.save()



