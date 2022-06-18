from .models import Subscription, SupportTask
from django.forms import ModelForm, DateTimeInput, TextInput, NumberInput, Form
from django import forms
from phonenumber_field.modelfields import PhoneNumberField

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
        fields = ('user', 'title', 'text', 'pub_date', 'email')

        widgets = {
            'pub_date': DateTimeInput(attrs={
                'type': 'hidden'
            }),
            'user': TextInput(attrs={
                'type': 'hidden'
            }),
        }

class ChangeUserInfoForm(Form):
    username = forms.CharField(max_length=250, label='Your name')
    email = forms.EmailField(max_length=250)

    class Meta:
        fields = ('username', 'email', )


class ChangeSubscibeStatusForm(Form):
    sub_id = forms.IntegerField()
    status_value = forms.IntegerField()

    class Meta:
        fields = ('sub_id', 'status_value')


class SubscribeCreateForm(Form):
    sub_id = forms.IntegerField()
    email = forms.EmailField()
    phone_number = PhoneNumberField()
    user_name = forms.CharField(max_length=250)
