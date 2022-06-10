from django.contrib import admin
from .models import Product, Rate, Subscription, Offer, User, Currency, SupportTask, PaymentType
from modeltranslation.admin import TranslationAdmin


class RateAdmin(TranslationAdmin):
    pass

class SubscriptionAdmin(TranslationAdmin):
    pass

class OfferAdmin(TranslationAdmin):
    pass

class CurrencyAdmin(TranslationAdmin):
    pass

class SupportTaskAdmin(TranslationAdmin):
    pass




class ProductAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Rate, RateAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Subscription)
admin.site.register(PaymentType)

