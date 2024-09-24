from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from weather.models import Subscription, City, Weather
from weather.forms import SubscriptionForm
from weather.tasks import get_weather_coordinates, get_weather_conditions


def home(request):
    return render(request, 'home.html')


@login_required
def create_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']

            result = get_weather_coordinates.delay(city_name)
            latitude, longitude, country = result.get()

            if not latitude or not longitude:
                form.add_error('city_name', f"City '{city_name}' does not exist in the weather service.")
                return render(request, 'create_subscription.html', {'form': form})

            city, created = City.objects.get_or_create(name=city_name, defaults={'country': country})

            subscription = form.save(commit=False)
            subscription.city = city
            subscription.user = request.user
            subscription.save()

            return redirect('weather:view_subscriptions')
    else:
        form = SubscriptionForm()

    return render(request, 'create_subscription.html', {'form': form})


@login_required
def view_subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'view_subscriptions.html', {'subscriptions': subscriptions})


def settings(request):
    return render(request, 'settings.html')


@login_required
def update_subscription(request, id):
    subscription = get_object_or_404(Subscription, id=id, user=request.user)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()
            return redirect('weather:view_subscriptions')
    else:
        form = SubscriptionForm(instance=subscription)

    return render(request, 'update_subscription.html', {'form': form})


@login_required
def delete_subscription(request, id):
    subscription = get_object_or_404(Subscription, id=id, user=request.user)

    if request.method == 'POST':
        subscription.delete()
        return redirect('weather:view_subscriptions')

    return render(request, 'delete_subscription.html', {'subscription': subscription})


@login_required
def subscription_detail(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)

    city = subscription.city
    weather_data = Weather.objects.filter(city=city).order_by('-time_getting').first()

    if not weather_data:
        coordinates_result = get_weather_coordinates.delay(city.name)
        coordinates = coordinates_result.get()

        if coordinates and all(coordinates):
            lat, lon, country = coordinates
            weather_result = get_weather_conditions.delay(lat, lon)
            weather_data = weather_result.get()

            if weather_data and all(weather_data):
                temperature, humidity, weather_description, time_getting = weather_data
                weather_data = {
                    'temperature': temperature,
                    'humidity': humidity,
                    'weather_description': weather_description,
                    'time_getting': time_getting,
                }
        else:
            weather_data = None

    return render(request, 'subscription_detail.html', {
        'subscription': subscription,
        'weather_data': weather_data
    })
