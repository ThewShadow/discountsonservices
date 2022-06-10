from .models import Subscription
from .models import Offer
from .models import Product
from .models import SupportTask
from django.contrib.auth.models import User
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)




def get_customer_subscriptions(customer_id):
    try:
        return Subscription.objects.filter(user__id=customer_id) or []
    except Exception as e:
        logger.error(e)


def get_offers_by_slug(slug):
    try:
        return Offer.objects.filter(product__slug=slug)
    except Exception as e:
        logger.error(e)



def send_support_task(task_id):
    try:
        task = SupportTask.objects.get(id=task_id)
        send_mail(
            task.title,
            task.text,
            'noreplyexample@mail.com',
            ['zvichayniy.vick@gmail.com'],
            fail_silently=False
        )
    except Exception as e:
        logger.error(e)


def notify_managers_of_new_subscription(subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Exception as e:
        logger.error(f'subscription not found {e}')
    else:
        try:
            send_mail(
                'new subscription',
                str(subscription),
                'noreplyexample@mail.com',
                ['zvichayniy.vick@gmail.com'],
                fail_silently=False
            )
        except Exception as e:
            logger.error(f'notify_managers error {e}')

def check_payment():
    pass


def gen_refer_link(user):
    pass


def create_payment(data):
    pass


def send_status_change_notification(user, data):
    pass


def senf_notification_new_subscription(data):
    pass


def get_refer_link(user):
    pass


