from django.shortcuts import redirect, get_object_or_404, render, HttpResponse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView, FormView, CreateView, TemplateView, View
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
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist


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

class ResetPasswordConfirmView(View):

    def post(self, request, **kwargs):
        form = ResetPasswordVerifyForm(request.POST)
        if form.is_valid():
            verify_code = form.cleaned_data.get('verify_code')

            verify_code_check = request.session.get('reset_pass_verify_code')
            if not verify_code_check:
                return JsonResponse({'success': False, 'message': 'Session expired'}, status=400)

            if str(verify_code) == verify_code_check:
                return JsonResponse({'success': True}, status=200)
            else:
                return JsonResponse({'success': False, 'message': 'invalid verification code'}, status=400)
        else:
            return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)

class ResetPasswordCompleteView(View):

    def post(self, request, **kwargs):
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            reset_pass_email = request.session.get('reset_pass_email')
            if not reset_pass_email:
                return JsonResponse({'success': False, 'message': 'Session expired'}, status=400)

            try:
                user = CustomUser.objects.get(email=reset_pass_email)
            except ObjectDoesNotExist:
                return JsonResponse({'success': False, 'message': 'User does not exist'}, status=400)
            else:
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                return JsonResponse({'success': True}, status=200)
        else:
            return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)

class ResetPasswordView(View):

    def post(self, request, **kwargs):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            reset_code = gen_verify_code()

            request.session['reset_pass_email'] = email
            request.session['reset_pass_verify_code'] = reset_code

            subject, from_email, to = 'Email verify', 'noreplyexample@mail.com', email
            html_content = f'<h1>Youre reset password code</h1><p>{reset_code}</p>'

            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.content_subtype = "html"
            msg.send()

            return JsonResponse({'success': True}, status=200)

        return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)


class IndexView(CommonMixin, ListView):
    template_name = 'main/index.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

class LogoutView(View):

    def post(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse_lazy('index'))

    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect(reverse_lazy('index'))


class LoginView(View):

    MESSAGES = {
        'error_verify': _('Email not verified'),
        'failed_auth': _('Wrong login or password')
    }

    def post(self, *args, **kwargs):

        form = LoginForm(self.request.POST)

        if not form.is_valid():
            return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)

        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(username=email, password=password)

        if user is None:
            return JsonResponse({'success': False, 'message': LoginView.MESSAGES['failed_auth']}, status=401)

        if not user.verified and not user.is_superuser:
            return JsonResponse({'success': False, 'message': LoginView.MESSAGES['error_verify']}, status=401)

        login(self.request, user)

        return JsonResponse({'success': True}, status=200)



class RegistrationView(View):
    class_form = CustomUserCreationForm

    def post(self, request, **kwargs):

        form = self.class_form(self.request.POST)

        if not form.is_valid():
            return JsonResponse(
                {
                    'success': False,
                    'error_messages': dict(form.errors)
                },
                status=400
            )

        user = form.save()

        verify_code = gen_verify_code()
        request.session['verify_email'] = user.email
        request.session['verify_code'] = verify_code

        subject, from_email, to = 'Email verify', 'noreplyexample@mail.com', form.cleaned_data['email']
        html_content = f'<h1>You verify code</h1><p>{verify_code}</p>'

        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.content_subtype = "html"
        msg.send()

        return JsonResponse({'success': True}, status=201)




class PayPalFormView(View):


    def post(self, *args, **kwargs):
        context = {'form': PayPalPaymentsForm(initial=self.get_payment_form())}
        template = render_to_string('main/paypal_form.html', context=context)
        return JsonResponse({"paypal_porm": template})

    def get_payment_form(self):
        test_url = 'https://729d-46-118-172-5.eu.ngrok.io'

        sub_id = self.request.POST.get('sub_id', None)
        lang = get_language().upper()
        sub_obj = get_object_or_404(Subscription, id=sub_id)

        return {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": sub_obj.offer.price,
            "currency_code": str(sub_obj.offer.currency.code).upper(),
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


class VerifyEmailView(View):

    def post(self, *args, **kwargs):
        form = VerifyEmailForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse({"success": False, 'message': 'Incorrect input data'}, status=400)

        verify_code = self.request.session.get('verify_code', None)
        verify_email = self.request.session.get('verify_email', None)

        if verify_code is None:
            return JsonResponse({"success": False, 'message': 'Session expired'}, status=400)
        else:
            if str(verify_code) == form.cleaned_data['verify_code']:
                try:
                    user = CustomUser.objects.get(email=verify_email)
                except:
                    return JsonResponse({"success": False, 'message': 'User is not found'}, status=400)
                else:
                    user.verified = True
                    user.save()
                    return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, 'message': 'Incorrect code'}, status=400)



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




#class SubscriptionCreateView(LoginRequiredMixin, CreateView):
class SubscriptionCreateView(View):
    #template_name = 'main/subscribe.html'
    # login_url = 'not_authorizate'
    # redirect_field_name = 'redirect_to'

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

            resp = {'success': True, 'sub_id': new_subscription.id}

            return JsonResponse(resp, status=200)
        else:
            return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)




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



def gen_verify_code():
    import random

    default_code_length = 6
    code_length = default_code_length if 'VERIFY_CODE_LENGTH' not in dir(settings) else settings.VERIFY_CODE_LENGTH
    result = ''
    for i in range(code_length):
        result += str(random.randint(3, 9))
    return result


def user_email_uniq(user, email):
    return CustomUser.objects.exclude(id=user.id).filter(email=email).count() == 0 \
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