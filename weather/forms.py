from django import forms
from .models import Subscription


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['city', 'notification_period']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-control'}),
            'notification_period': forms.Select(attrs={'class': 'form-control'}),
        }
