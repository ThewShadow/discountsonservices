from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from main.models import Subscription
from config import settings

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):

    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
            # Not a valid payment
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.
        try:
            sub_obj = Subscription.objects.get(id=ipn_obj.invoice)
            assert ipn_obj.mc_gross == sub_obj.offer.price
            sub_obj.status = 2
            sub_obj.save()
        except Exception:
            pass
        else:
            pass
    else:
        pass
