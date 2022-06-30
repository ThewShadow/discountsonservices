import service.service as service
from django.shortcuts import redirect, get_object_or_404, render, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View
from paypal.standard.forms import PayPalPaymentsForm
from main.models import CustomUser
from main.models import Offer
from main.models import Subscription
from main.forms import LoginForm
from main.forms import SubscribeCreateForm
from main.forms import VerifyEmailForm
from main.forms import CustomUserCreationForm
from main.forms import ResetPasswordForm
from main.forms import ResetPasswordVerifyForm
from main.forms import NewPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
import logging
from service import crypto
from service import google
from service import paypal
import threading



class SubscriptionCreate(View):

    def post(self, request, **kwargs):
        form = SubscribeCreateForm(self.request.POST)
        if form.is_valid():
            offer = get_object_or_404(Offer, id=form.cleaned_data['offer_id'])

            try:
                new_subscription = Subscription.objects.get(
                    offer__id=offer.id,
                    user=self.request.user,
                    email=form.cleaned_data['email'],
                    paid=False)

            except Exception as e:

                new_subscription = Subscription()
                new_subscription.email = form.cleaned_data['email']
                new_subscription.phone_number = form.cleaned_data['phone_number']
                new_subscription.offer = offer
                new_subscription.user_name = form.cleaned_data['user_name']
                new_subscription.user = self.request.user

                try:
                    new_subscription.save()
                    thread = threading.Thread(target=new_subscription.notify_managers)
                    thread.start()
                    #new_subscription.notify_managers()
                except Exception as e:
                    print(e)

            finally:
                if new_subscription:
                    resp = {'success': True, 'sub_id': new_subscription.id}
                    request.session['current_offer_id'] = form.cleaned_data['offer_id']
                    return JsonResponse(resp, status=200)
                else:
                    return JsonResponse({'success': False}, status=400)
        else:
            return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)


class CryptoPayCreate(View):

    def post(self, request, **kwargs):
        type_payment = request.POST.get('type-payment')
        type_blockchain = request.POST.get('type-blockchain')

        if type_payment and type_blockchain:
            link = crypto.gen_crypto_pay_link(type_payment, type_blockchain)

            offer_id = request.session.get('current_offer_id')
            amount = Offer.objects.get(id=offer_id).price

            curr = None
            if 'Bitcoin' in type_payment:
                curr = 'BTC'
            elif 'Ethereum' in type_payment:
                curr = 'ETH'

            if curr:
                crypto_amount = crypto.get_crypto_amount(curr, amount)
            else:
                crypto_amount = amount + ' USDT'

            response = {
                'success': True,
                'payment_link': link,
                'blockchain_name': str(type_blockchain).replace('Blockchain', ''),
                'amount': crypto_amount
            }

            return JsonResponse(response)
        else:
            return JsonResponse({'success': False, 'message': 'Bad Request'}, status=400)


class GoogleLogin(View):

    def get(self, request, **kwargs):
        url = google.gen_auth_url()
        return HttpResponseRedirect(url)


class GoogleLoginComplete(View):

    def get(self, request, **kwargs):
        code = request.GET.get('code')
        if not code:
            return redirect(reverse_lazy('index'))

        access_token = google.get_user_auth_token(code)

        user_info = google.get_user_info(access_token)

        try:
            user = CustomUser.objects.get(email=user_info['email'])
        except ObjectDoesNotExist:
            user = CustomUser()
            user.email = user_info['email']
            user.username = user_info['given_name']
            user.save()
        finally:
            login(self.request, user, backend='main.backends.EmailBackend')

        return redirect(reverse_lazy('profile'))


class PayPalCreate(View):

    def post(self, request, **kwargs):
        context = {'form': PayPalPaymentsForm(initial=paypal.get_payment_form(request))}
        template = render_to_string('main/paypal_form.html', context=context)
        return JsonResponse({"paypal_porm": template})


class Login(View):

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
            return JsonResponse({'success': False, 'message': Login.MESSAGES['failed_auth']}, status=401)

        if not user.verified and not user.is_superuser:
            return JsonResponse({'success': False, 'message': Login.MESSAGES['error_verify']}, status=401)

        login(self.request, user)

        return JsonResponse({'success': True}, status=200)


class Registration(View):
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

        verify_code = service.gen_verify_code()
        request.session['verify_email'] = user.email
        request.session['verify_code'] = verify_code

        subject, from_email, to = 'Email verify', 'noreplyexample@mail.com', form.cleaned_data['email']
        html_content = f'<h1>You verify code</h1><p>{verify_code}</p>'

        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.content_subtype = "html"
        msg.send()

        return JsonResponse({'success': True}, status=201)


class ResetPasswordConfirm(View):

    def post(self, request, **kwargs):
        form = ResetPasswordVerifyForm(request.POST)
        if form.is_valid():
            verify_code = form.cleaned_data.get('verify_code')

            verify_code_check = request.session.get('reset_pass_verify_code')
            if not verify_code_check:
                return JsonResponse(
                    {'success': False, 'message': 'Session expired'}, status=400)

            if str(verify_code) == verify_code_check:
                return JsonResponse({'success': True}, status=200)
            else:
                return JsonResponse({'success': False, 'message': 'invalid verification code'}, status=400)
        else:
            return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)


class ResetPasswordComplete(View):

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


class ResetPassword(View):

    def post(self, request, **kwargs):

        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            reset_code = service.gen_verify_code()

            request.session['reset_pass_email'] = email
            request.session['reset_pass_verify_code'] = reset_code

            subject, from_email, to = 'Email verify', 'noreplyexample@mail.com', email
            html_content = f'<h1>Youre reset password code</h1><p>{reset_code}</p>'

            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.content_subtype = "html"
            msg.send()

            return JsonResponse({'success': True}, status=200)

        return JsonResponse({'success': False, 'error_messages': dict(form.errors)}, status=400)


class VerifyEmail(View):

    def post(self, *args, **kwargs):
        form = VerifyEmailForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse({"success": False, 'message': 'Incorrect input data'}, status=400)

        verify_code = self.request.session.get('verify_code', None)
        verify_email = self.request.session.get('verify_email', None)

        if verify_code is None:
            return JsonResponse({"success": False, 'message': 'Session expired'}, status=400)
        else:
            if str(verify_code) == str(form.cleaned_data['verify_code']):
                try:
                    user = CustomUser.objects.get(email=verify_email)
                except ObjectDoesNotExist:
                    return JsonResponse({"success": False, 'message': 'User is not found'}, status=400)
                else:
                    user.verified = True
                    user.save()
                    return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, 'message': 'Incorrect code'}, status=400)



