from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver
from main.models import Subscription
from config import settings
from paypal.standard.ipn.models import PayPalIPN
import logging

logger = logging.getLogger(__name__)


@receiver(valid_ipn_received, sender=PayPalIPN)
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
            subscr_obj = Subscription.objects.get(id=ipn_obj.invoice)
        except:
            logger.warning(f'Payment accepted but subscription ({ipn_obj.invoice}) not found')

        try:
            assert ipn_obj.mc_gross == subscr_obj.offer.price
        except:
            logger.warning('Payment amount does not match the offer price.'
                           f'summ: {ipn_obj.mc_gross}'
                           f'invoice: {ipn_obj.invoice}')

        else:
            subscr_obj.paid = True
            try:
                subscr_obj.save()
            except Exception:
                logger.error('The subscription is paid, but it was not possible to set the paid flag'
                             f'invoice: {ipn_obj.invoice}')
            else:
                logger.info(f'Subscription ({ipn_obj.invoice}) is paid.')
    else:
        logger.info(f'Subscription ({ipn_obj.invoice}) not paid. status {str(ST_PP_COMPLETED)}')

