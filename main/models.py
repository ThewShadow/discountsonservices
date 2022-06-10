from django.db import models
from django.contrib.auth.models import User

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
    email = models.CharField(max_length=250, default='')
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=15, default='')

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


class SupportTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    text = models.TextField()
    pub_date = models.DateTimeField()

    def __str__(self):
        return f'{self.pub_date} {self.user} {self.title}'



