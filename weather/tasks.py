from celery import shared_task
import logging
import redis
from django.utils import timezone
import requests
from .models import Weather, City
from pathlib import Path
from dotenv import dotenv_values
import json
from base.settings import REDIS_HOST, REDIS_PORT

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
