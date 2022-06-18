from django.apps import AppConfig
from django.core.signals import request_finished,request_started

from paypal.standard.ipn.signals import valid_ipn_received



class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):

        from main import hooks
        from paypal.standard.ipn.models import PayPalIPN
        request_started.connect(hooks.paypal_payment_received, sender=PayPalIPN)