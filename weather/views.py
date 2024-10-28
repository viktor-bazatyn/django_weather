from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from weather.models import Subscription, City, Weather
from weather.forms import SubscriptionForm
from weather.tasks import get_weather_coordinates, get_weather_conditions
from rest_framework import generics, permissions, status
from .serializers import SubscriptionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import localtime


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

    if weather_data:
        weather_data = {
            'temperature': weather_data.temperature,
            'humidity': weather_data.humidity,
            'weather_description': weather_data.weather_description,
            'time_getting': localtime(weather_data.time_getting).isoformat(),  # Формат ISO 8601
        }
    else:
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
                    'time_getting': time_getting.isoformat() if time_getting else None,
                }
        else:
            weather_data = None

    return render(request, 'subscription_detail.html', {
        'subscription': subscription,
        'weather_data': weather_data
    })


class SubscriptionCreate(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionList(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionDeleteCity(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete_city(self, request):
        city_name = request.data.get("city_name")

        if not city_name:
            return Response({"detail": "City name is required."}, status=status.HTTP_400_BAD_REQUEST)

        city = City.objects.filter(name=city_name).first()
        if not city:
            return Response({"detail": "City not found."}, status=status.HTTP_404_NOT_FOUND)

        subscription = Subscription.objects.filter(user=request.user, city=city).first()
        if not subscription:
            return Response({"detail": f"No subscription found for city: {city_name}"},
                            status=status.HTTP_404_NOT_FOUND)

        subscription.delete()
        return Response({"detail": "Subscription deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class CityWeatherDetailApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        city_name = request.query_params.get("city_name", None)
        if not city_name:
            return Response({"detail": "City name is required."}, status=status.HTTP_400_BAD_REQUEST)

        city, _ = City.objects.get_or_create(name=city_name)
        weather_data = Weather.objects.filter(city=city).order_by('-time_getting')
        if not weather_data:
            coordinates_result = get_weather_coordinates.delay(city.name)
            coordinates = coordinates_result.get(timeout=15)
            if coordinates and all(coordinates):
                lat, lon, country = coordinates
                weather_result = get_weather_conditions.delay(lat, lon)
                weather_data = weather_result.get(timeout=15)

                if weather_data and all(weather_data):
                    temperature, humidity, weather_description, time_getting = weather_data
                    data = {
                        'city': f"{city.name} {country}",
                        'temperature': temperature,
                        'humidity': humidity,
                        'weather_description': weather_description,
                        'time_getting': time_getting,
                    }
                else:
                    return Response({"detail": f"No weather data found for city: {city.name}"},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'detail': f'Coordinates not found for city: {city.name}'},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            data = {
                'city': f"{city.name} {city.country}",
                'temperature': weather_data.temperature,
                'humidity': weather_data.humidity,
                'weather_description': weather_data.weather_description,
                'time_getting': weather_data.time_getting,
            }
        return Response(data, status=status.HTTP_200_OK)


class UpdateSubscription(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        city_name = request.data.get("city_name", None)
        notification_period = request.data.get("notification_period", None)
        if not city_name or not notification_period:
            return Response({"deatil": f'City name and notification period is required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        city = get_object_or_404(City, name=city_name)
        subscription = get_object_or_404(Subscription, user=request.user, city=city)
        subscription.notification_period = notification_period
        subscription.save()
        return Response({"detail": "Subscription updated successfully."}, status=status.HTTP_200_OK)
