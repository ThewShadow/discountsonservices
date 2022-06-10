from django.forms import ModelForm
from .models import Subscription, SupportTask
from django.forms import ModelForm, DateTimeInput, TextInput, NumberInput



class SubscribeForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ('offer', 'status', 'email', 'user', 'phone_number','payment_type',)

        widgets = {
            'status': NumberInput(attrs={
                'type': 'hidden'
            }),
            'user': TextInput(attrs={
                'type': 'hidden'
            }),
        }


class SupportCreateTaskForm(ModelForm):
    class Meta:
        model = SupportTask
        fields = ('user', 'title', 'text', 'pub_date')

        widgets = {
            'pub_date': DateTimeInput(attrs={
                'type': 'hidden'
            }),
            'user': TextInput(attrs={
                'type': 'hidden'
            }),
        }
