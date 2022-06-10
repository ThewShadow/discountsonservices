from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from .models import Offer, Subscription, Product, Rate
from django.views.generic import ListView, DetailView, FormView, CreateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import SubscribeForm, SupportCreateTaskForm
from datetime import datetime
from . import service


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
                return redirect(reverse_lazy('offers', kwargs={'slug': product_slug, 'rate_slug': rate_slug}))

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = get_object_or_404(Product, slug=self.kwargs.get('slug'))

        rate_slug = self.kwargs.get('rate_slug', None)

        if rate_slug:
            context['rate_slug'] = rate_slug
            context['offers'] = Offer.objects.filter(product__slug=self.kwargs.get('slug'), rate__slug=rate_slug)

            context['rates'] = Offer.objects.filter(product__slug=self.kwargs.get('slug')).order_by('price')

        else:
            context['offers'] = Offer.objects.filter(product__slug=self.kwargs.get('slug'))


        return context

class SubscriptionCreateView(LoginRequiredMixin, CreateView):
    template_name = 'main/subscribe.html'
    model = Subscription
    form_class = SubscribeForm
    login_url = 'not_authorizate'
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy('profile')

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        initial['email'] = self.request.user.email

        initial['offer'] = get_object_or_404(Offer, id=self.kwargs.get('offer_id'))

        return initial

    def form_valid(self, form):
        subscription = form.save(commit=True)
        service.notify_managers_of_new_subscription(subscription.id)

        return redirect(reverse_lazy('profile'))


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'main/user_profile.html'
    model = User
    login_url = 'not_authorizate'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_subscriptions'] = Subscription.objects.filter(
            user__id=self.request.user.id)

        return context

    def get_object(self, queryset=None):
        return get_object_or_404(User, id=self.request.user.id)


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

class PaymentViiew(TemplateView):


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


    # def post(self, request, *args, **kwargs):
    #     form = SupportCreateTaskForm(request.POST)
    #     if form.is_valid():
    #         form.save(commit=True)
    #
    #     return redirect(reverse('index'))


def get_(product_id):
   pass
