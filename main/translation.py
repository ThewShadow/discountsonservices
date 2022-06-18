from modeltranslation.translator import translator, TranslationOptions
from .models import Offer, Rate, Subscription, Product, SupportTask, Currency


class RateTranslationOptions(TranslationOptions):
    fields = ('name',)

class OfferTranslationOptions(TranslationOptions):
    fields = ('name',)

class ProductTranslationOptions(TranslationOptions):
    fields = ('name',)

class CurrencyTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Offer, OfferTranslationOptions)
translator.register(Currency, CurrencyTranslationOptions)
translator.register(Product, ProductTranslationOptions)
translator.register(Rate, OfferTranslationOptions)
