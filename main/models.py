from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Rate(models.Model):
    name = models.CharField(max_length=200, default='')
    count = models.IntegerField()
    slug = models.SlugField(default='')

    def __str__(self):
        return f'{self.count} {self.name}'

class Currency(models.Model):
    name = models.CharField(max_length=40, default='')
    code = models.CharField(max_length=4, default='')

    def __str__(self):
        return f'{self.name} ({self.code})'


class FAQ(models.Model):
    title = models.CharField(max_length=200, default='')
    answer = models.TextField(null=True)

class Offer(models.Model):
    name = models.CharField(max_length=200, default='')
    rate = models.ForeignKey('Rate', on_delete=models.CASCADE, null=True)
    price = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE, null=True)
    description = models.TextField(null=True)


    def __str__(self):
        return f'{self.product.name} - {self.name} - {self.rate}: {self.price} {self.currency.code}'


class Product(models.Model):
    name = models.CharField(max_length=200, default='')
    slug = models.SlugField(default='')
    multi_plane = models.BooleanField(default=False)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

class PaymentType(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, null=True)
    email = models.EmailField(max_length=250)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, null=True)
    phone_number = PhoneNumberField(null=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True)

    STATUSES = [
        (1, 'being processed'),
        (2, 'done'),
        (3, 'canceled'),
    ]
    status = models.IntegerField(
        choices=STATUSES,
        default=1,
    )

    def __str__(self):
        return f'{self.user} - {self.offer}'


    def notify_managers(self):
        from config.settings import MANAGERS_EMAILS
        from django.core.mail import EmailMultiAlternatives

        subject, from_email, to = 'New subscription', 'noreplyexample@mail.com', MANAGERS_EMAILS
        html_content = Subscription.generate_message_for_managers(self)

        msg = EmailMultiAlternatives(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()

    def notify_user(self):
        from django.core.mail import EmailMultiAlternatives

        subject, from_email, to = 'New subscription', 'noreplyexample@mail.com', [self.user.email]
        html_content = Subscription.generate_message_for_user(self)

        msg = EmailMultiAlternatives(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()

    @staticmethod
    def generate_message_for_managers(subscription):
        data = [
            f'<h3>You have a new subscription order (id: {subscription.id})</h3>',
            f'<p>Plan: {str(subscription.offer)}</p>',
            f'<p>User id: {subscription.user.id}</p>',
            f'<p>User email: {subscription.email}</p>',
            f'<p>Phone number: {subscription.phone_number}</p>',
            f'<p>Paynment type: {subscription.payment_type}</p>',
            f'<p>Order date: {subscription.order_date.strftime("%d/%m/%y %H:%M")}</p>'
        ]
        return '\n'.join(data)

    @staticmethod

    def generate_message_for_user(subscription):
        pass



class SupportTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    text = models.TextField()
    pub_date = models.DateTimeField()
    email = models.EmailField(default='')

    def __str__(self):
        return f'{self.pub_date} {self.user} {self.title}'



