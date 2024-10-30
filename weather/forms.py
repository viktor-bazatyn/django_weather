from django import forms
from .models import Subscription
from weather.tasks import get_weather_coordinates
from pytz import all_timezones


class SubscriptionForm(forms.ModelForm):
    city_name = forms.CharField(max_length=100, label="City",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}))
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in all_timezones],
        label="Select Timezone",
        required=True
    )

    class Meta:
        model = Subscription
        fields = ['city_name', 'notification_period', 'timezone']
        widgets = {
            'notification_period': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_city_name(self):
        city_name = self.cleaned_data.get('city_name').strip()
        result = get_weather_coordinates.delay(city_name)
        latitude, longitude, country = result.get()

        if not latitude or not longitude:
            raise forms.ValidationError(f"City '{city_name}' does not exist in the weather service.")
        return city_name
