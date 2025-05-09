from celery import shared_task
import logging
import redis
from django.template.loader import render_to_string
from django.utils import timezone
import requests
from django.utils.html import strip_tags

from base import settings
from .models import Weather, City, Subscription
from pathlib import Path
from dotenv import dotenv_values
import json
from base.settings import REDIS_HOST, REDIS_PORT
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.core.mail import send_mail
from pytz import timezone as pytz_timezone

BASE_DIR = Path(__file__).resolve().parent.parent
config = dotenv_values(BASE_DIR / ".env")
API_KEY = config.get('OPENWEATHER_API_KEY')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_instance = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
CACHE_TIME = 15 * 60


@shared_task
def get_weather_coordinates(city_name):
    cache_key = f'coordinates:{city_name}'
    cached_data = redis_instance.get(cache_key)

    if cached_data:
        logger.info(f"Returning cached coordinates for {city_name}")
        return json.loads(cached_data)

    API_URL = f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={API_KEY}'
    response = requests.get(API_URL)

    if response:
        data = response.json()
        if data:
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            country = data[0]['country']
            redis_instance.setex(cache_key, CACHE_TIME, json.dumps([latitude, longitude, country]))
            logger.info(f"Coordinates for {city_name} fetched from API and cached")
            return latitude, longitude, country
        else:
            logger.info('No weather data in the city')
            return None, None, None
    else:
        logger.info(f"Error: {response.status_code}, {response.text}")
        return None, None, None


@shared_task
def get_weather_conditions(latitude, longitude):
    cache_key = f"weather:{latitude}:{longitude}"
    cached_data = redis_instance.get(cache_key)
    if cached_data:
        logger.info(f"Returning cached weather data for {latitude}, {longitude}")
        return json.loads(cached_data)

    API_URL = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric'
    response = requests.get(API_URL)

    if response:
        data = response.json()
        if data:
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            weather_description = data['weather'][0]['description']
            time_getting = timezone.now()
            redis_instance.setex(cache_key, CACHE_TIME,
                                 json.dumps([temperature, humidity, weather_description, str(time_getting)]))
            logger.info(f"Weather data for {latitude}, {longitude} fetched from API and cached")
            return temperature, humidity, weather_description, time_getting
        else:
            logger.info('No weather data available.')
            return None, None, None, None
    else:
        logger.info(f"Error: {response.status_code}, {response.text}")
        return None, None, None, None


@shared_task
def save_weather_data(city_name, country, temperature, humidity, weather_description, time_getting):
    try:

        city, created = City.objects.get_or_create(name=city_name, defaults={'country': country})
        if created:
            logger.info(f'City {city_name} in {country} created successfully')
        else:
            if city.country != country:
                city.country = country
                city.save()
                logger.info(f'City {city_name} updated with new country {country}.')

        weather_data = Weather(
            city=city,
            temperature=temperature,
            humidity=humidity,
            weather_description=weather_description,
            time_getting=time_getting
        )
        weather_data.save()
        logger.info(f'Weather data for {city.name}, {city.country} saved successfully')
    except Exception as e:
        logger.error(f"An error occurred while saving the weather data: {e}")


def get_weather_icon(description):
    description = description.lower()
    if 'clear sky' in description:
        return 'https://cdn-icons-png.flaticon.com/512/869/869869.png'
    elif ('broken clouds' in description or 'scattered clouds' in description or 'overcast clouds' in description
          or 'few clouds' in description):
        return 'https://cdn-icons-png.flaticon.com/512/414/414825.png'
    elif 'light rain' in description:
        return 'https://openweathermap.org/img/wn/10d@2x.png'
    else:
        return 'https://openweathermap.org/img/wn/50d@2x.png'


@shared_task
def update_weather_for_all_cities():
    logger.info("Task 'update_weather_for_all_cities' started.")
    cities = City.objects.all()

    for city in cities:
        latitude, longitude, country = get_weather_coordinates(city.name)
        if not latitude or not longitude or not country:
            logger.info(f'No coordinates for {city.name}')
            continue

        temperature, humidity, weather_description, time_getting = get_weather_conditions(latitude, longitude)
        if temperature and humidity and weather_description:
            save_weather_data.delay(city.name, country, temperature, humidity, weather_description, time_getting)
            logger.info(f"Weather data for city {city.name} updated and cached in Redis.")

            subscriptions = Subscription.objects.filter(city=city)
            for subscription in subscriptions:
                if subscription.last_notified is None or \
                        (timezone.now() - subscription.last_notified).total_seconds() >= subscription.notification_period * 3600:

                    user_timezone = subscription.timezone or 'UTC'
                    tz = pytz_timezone(user_timezone)

                    local_time = time_getting.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')

                    context = {
                        'city_name': city.name,
                        'user_email': subscription.user.first_name,
                        'weather_description': weather_description,
                        'temperature': temperature,
                        'humidity': humidity,
                        'time_getting': local_time,
                        'weather_icon': get_weather_icon(weather_description)
                    }

                    html_message = render_to_string('weather_email.html', context)
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject=f'Weather Update for {city.name}',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscription.user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    subscription.last_notified = timezone.now()
                    subscription.save()

                    logger.info(f"Weather update email sent to {subscription.user.email} for city {city.name}")
        else:
            logger.error(f"Failed to get weather data for city: {city.name}")

    logger.info("Task 'update_weather_for_all_cities' finished.")


def schedule_weather_reminder():
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=15,
        period=IntervalSchedule.MINUTES,
    )
    PeriodicTask.objects.create(
        interval=schedule,
        name='Update weather data every 15 minutes',
        task='weather.tasks.update_weather_for_all_cities',
    )
    logger.info("Scheduled periodic task 'Update weather data every 15 minutes' successfully.")
