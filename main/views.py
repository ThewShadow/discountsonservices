from django.shortcuts import redirect, get_object_or_404, render, HttpResponse
from django.urls import reverse_lazy
from django.http import JsonResponse
from httplib2 import Http
from django.template.loader import render_to_string
from .models import Offer, Subscription, Product, FAQ
from django.views.generic import ListView, FormView, CreateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import RegistrationForm, SupportCreateTaskForm, ChangeUserInfoForm, ChangeSubscibeStatusForm, SubscribeCreateForm, VerifyEmailForm
from datetime import datetime
from . import service
from social_django.models import UserSocialAuth
from django.core.exceptions import PermissionDenied
from paypal.standard.forms import PayPalPaymentsForm
from config import settings
from django.utils.translation import get_language
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser




class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

class LogoutView(View):

    def post(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse_lazy('index'))

    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse_lazy('index'))


class LoginView(View):
    form_class = LoginForm

    def post(self, *args, **kwargs):
        form = LoginForm(self.request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(self.request, user)
                return JsonResponse({'success': True}, status=200)

            return JsonResponse({'success': False, 'error_messages': ['Perrmision Denied']}, status=401)

        return JsonResponse({'success': False, 'error_messages': form.errors}, status=401)

    def get(self):
        return HttpResponse('<h1>Method Not Allowed</h1>', status=406)



class RegistrationView(View):

    def post(self, *args, **kwargs):
        form = RegistrationForm(self.request.POST)
        if form.is_valid():
            try:
                CustomUser.objects.get(email=form.cleaned_data['email'])
                return JsonResponse({'success': False, 'error_messges': 'User is exist'}, status=406)
            except:
                user = User(username=form.cleaned_data['username'],
                     password=form.cleaned_data['password'],
                     email=form.cleaned_data['email'])
                user.save()

                verify_code = 448866
                self.request.session['verify_email'] = form.cleaned_data['email']
                self.request.session['verify_code'] = verify_code

                from django.core.mail import EmailMultiAlternatives

                subject, from_email, to = 'Email verify', 'noreplyexample@mail.com', form.cleaned_data['email']
                html_content = f'<h1>You verify code</h1><p>{verify_code}</p>'

                msg = EmailMultiAlternatives(subject, html_content, from_email, to)
                msg.content_subtype = "html"
                msg.send()

                return JsonResponse({'success': True, 'verify_email': form.cleaned_data['email']})

        return JsonResponse({'success': False, 'error_messages': form.errors})


class CommonMixin:

    def get_common_data(self, request, **kwargs):
        kwargs['all_products'] = Product.objects.all()
        kwargs['login_form'] = LoginForm()
        kwargs['register_form'] = RegistrationForm()
        kwargs['verify_email_form'] = VerifyEmailForm()

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        common = self.get_common_data(self.request, **kwargs)

        return dict(list(context.items()) + list(common.items()))


class PayPalFormView(View):

    def get(self, *args, **kwargs):
        return HttpResponse('Method Not Allowed', status=406)

    def post(self, *args, **kwargs):
        context = {'form': PayPalPaymentsForm(initial=self.get_payment_form())}
        template = render_to_string('main/paypal_form.html', context=context)
        return JsonResponse({"form": template})

    def get_payment_form(self):
        test_url = 'https://729d-46-118-172-5.eu.ngrok.io'

        sub_id = self.request.POST.get('sub_id', None)
        lang = get_language().upper()
        sub_obj = get_object_or_404(Subscription, id=sub_id)

        return {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": sub_obj.offer.price,
            "currency_code": sub_obj.offer.currency.code,
            "item_name": 'test',
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


class IndexView(CommonMixin, ListView):
    template_name = 'main/index.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

class OffersView(CommonMixin, ListView):
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




#class SubscriptionCreateView(LoginRequiredMixin, CreateView):
class SubscriptionCreateView(View):
    #template_name = 'main/subscribe.html'
    # login_url = 'not_authorizate'
    # redirect_field_name = 'redirect_to'

    def get(self, *args, **kwargs):
        return HttpResponse('Method Not Allowed', status=406)

    def post(self, *args, **kwargs):
        form = SubscribeCreateForm(self.request.POST)
        if form.is_valid():
            offer = get_object_or_404(Offer, id=form.cleaned_data['offer_id'])
            new_subscription = Subscription()
            new_subscription.email = form.cleaned_data['email']
            new_subscription.phone_number = form.cleaned_data['phone_number']
            new_subscription.offer = offer
            new_subscription.user_name = form.cleaned_data['user_name']
            try:
                new_subscription.save()
            except Exception as e:
                print(e)

            resp = {'sub_id': new_subscription.id}

            return JsonResponse(resp, status=200)
        else:
            return JsonResponse({'error': True}, status=400)




class ProfileView(CommonMixin, LoginRequiredMixin, FormView):
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

class FAQView(CommonMixin, ListView):
    model = FAQ
    template_name = 'main/faq.html'
    context_object_name = 'questions_list'


class PayPalPaymentCancelView(CommonMixin, TemplateView):
    template_name = 'payments/paypal_cancel.html'

class PayPalPaymentReturnView(CommonMixin, TemplateView):
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