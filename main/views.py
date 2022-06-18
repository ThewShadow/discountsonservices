from django.shortcuts import redirect, get_object_or_404, render, HttpResponse
from django.urls import reverse_lazy
from httplib2 import Http

from .models import Offer, Subscription, Product, FAQ
from django.views.generic import ListView, FormView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import SubscribeForm, SupportCreateTaskForm, ChangeUserInfoForm, ChangeSubscibeStatusForm, SubscribeCreateForm
from datetime import datetime
from . import service
from social_django.models import UserSocialAuth
from django.core.exceptions import PermissionDenied
from paypal.standard.forms import PayPalPaymentsForm
from config import settings
from django.utils.translation import get_language


class PaypalFormView(FormView):
    template_name = 'payments/paypal_form.html'
    form_class = PayPalPaymentsForm

    def get(self, request, **kwargs):

        if not self.request.session.get('sub_id', None):
            return HttpResponse('error', status=406)

        form = self.form_class(initial=self.get_initial())
        return render(request, template_name=self.template_name, context={'form': form})

    def get_initial(self):
        test_url =  'https://729d-46-118-172-5.eu.ngrok.io'

        lang = get_language().upper()
        sub_id = self.request.session.get('sub_id', None)
        sub_obj = get_object_or_404(Subscription, id=sub_id)

        return {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": sub_obj.offer.price,
            "currency_code": sub_obj.offer.currency.code,
            "item_name": f'{sub_obj.offer.product.name} {sub_obj.offer.name}',
            "invoice": sub_id,
            # "notify_url": self.request.build_absolute_uri(reverse_lazy('paypal-ipn')),
            # "return_url": self.request.build_absolute_uri(reverse_lazy('paypal_return')),
            # "cancel_return": self.request.build_absolute_uri(reverse_lazy('paypal_cancel')),
            "notify_url": test_url + reverse_lazy('paypal-ipn'),
            "return_url": test_url + reverse_lazy('paypal_return'),
            "cancel_return": test_url + reverse_lazy('paypal_cancel'),
            "lc": lang,
            "no_shipping": '1',
        }

class IndexView(ListView):
    template_name = 'main/index.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

class OffersView(ListView):
    template_name = 'main/offers.html'
    model = Offer

    def get(self, *args, **kwargs):
        rate_slug = self.kwargs.get('rate_slug', None)
        if not rate_slug:
            product_slug = self.kwargs.get('slug', None)
            offers = Offer.objects.filter(product__slug=product_slug)

            min_offer = offers.order_by('price').first()
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




class SubscriptionCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/subscribe.html'
    model = Subscription
    form_class = SubscribeForm
    login_url = 'not_authorizate'
    redirect_field_name = 'redirect_to'
    #success_url = reverse_lazy('profile')



    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        initial['email'] = self.request.user.email
        initial['offer'] = get_object_or_404(Offer, id=self.kwargs.get('offer_id'))
        return initial

    def form_valid(self, form):
        subscription = form.save(commit=True)
        subscription.notify_managers()
        self.request.session['sub_id'] = subscription.id
        return redirect(reverse_lazy('paypal_order_create'))

class ProfileView(LoginRequiredMixin, FormView):
    template_name = 'main/user_profile.html'
    login_url = 'not_authorizate'
    redirect_field_name = 'redirect_to'
    form_class = ChangeUserInfoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user_inst = self.request.user
        initial_data = {'username': user_inst.username, 'email': user_inst.email}
        context['object'] = get_object_or_404(User, id=self.request.user.id)
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

class NotAuthorizate(TemplateView):
    template_name = 'main/not_authorizate.html'

class SupportView(LoginRequiredMixin, CreateView):
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

class AboutUsView(TemplateView):
    template_name = 'main/about_us.html'

class UserSubscriptionsView(LoginRequiredMixin, ListView):
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

class ManagerPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'main/manager_panel.html'

    def get(self, request, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied()

        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        form = ChangeSubscibeStatusForm(request.POST)
        if form.is_valid():
            obj = get_object_or_404(Subscription, id=form.cleaned_data['sub_id'])
            obj.status = form.cleaned_data['status_value']
            obj.save()
            obj.notify_user()

        return redirect(reverse_lazy('manager_panel'))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_subscriptions'] = Subscription.objects.filter(status=1).order_by('-order_date')
        context['all_statuses'] = Subscription.STATUSES
        return context

class FAQView(ListView):
    model = FAQ
    template_name = 'main/faq.html'
    context_object_name = 'questions_list'


class PayPalPaymentCancelView(TemplateView):
    template_name = 'payments/paypal_cancel.html'

class PayPalPaymentReturnView(TemplateView):
    template_name = 'payments/paypal_return.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.request.session.get('sub_id', None)
        return context




def user_email_uniq(user, email):
    return User.objects.exclude(id=user.id).filter(email=email).count() == 0 \
           and UserSocialAuth.objects.exclude(user=user).filter(uid=email).count() == 0


def change_profile_info(request, form):
    user = request.user
    user.username = form.cleaned_data.get('username')
    new_email = form.cleaned_data.get('email')

    from django.contrib import messages

    if user_email_uniq(user, new_email):
        user.email = new_email
        user.save()
        try:
            social_user = UserSocialAuth.objects.get(user__id=request.user.id)
        except:
            pass
        else:
            social_user.uid = new_email
            social_user.save()

        messages.add_message(request, messages.INFO, 'Profile info is update.')
    else:
        messages.add_message(request, messages.ERROR, 'User with this email is exist! Enter the other email')