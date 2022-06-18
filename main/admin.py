from django.contrib import admin
from .models import Product, Rate, Subscription, Offer, Currency, SupportTask, PaymentType, FAQ
from modeltranslation.admin import TranslationAdmin


class RateAdmin(TranslationAdmin):
    pass

class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ('order_date',)

class OfferAdmin(TranslationAdmin):
    pass

class CurrencyAdmin(TranslationAdmin):
    pass


class ProductAdmin(TranslationAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Rate, RateAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(SupportTask)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(PaymentType)
admin.site.register(FAQ)


