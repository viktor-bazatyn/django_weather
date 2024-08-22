import os
import django
import requests
from django.utils import timezone
from dotenv import dotenv_values
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

from weather.tasks import save_weather_data

BASE_DIR = Path(__file__).resolve().parent.parent
config = dotenv_values(BASE_DIR / ".env")
API_KEY = config.get('OPENWEATHER_API_KEY')


def get_weather_coordinates(city_name):
    API_URL = f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={API_KEY}'
    response = requests.get(API_URL)

    if response:
        data = response.json()
        if data:
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            country = data[0]['country']
            return latitude, longitude, country
        else:
            print('No weather data in the city')
            return None, None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None, None


def get_weather_conditions(latitude, longitude):
    API_URL = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric'
    response = requests.get(API_URL)

    if response:
        data = response.json()
        if data:
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            weather_description = data['weather'][0]['description']
            time_getting = timezone.now()
            return temperature, humidity, weather_description, time_getting
        else:
            print('No weather data available.')
            return None, None, None, None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None, None, None, None


city_name = input('Enter city name: ')
lat, lon, country = get_weather_coordinates(city_name)

if lat is not None and lon is not None:
    temperature, humidity, weather_description, time_getting = get_weather_conditions(lat, lon)
    if temperature is not None:
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%, Weather: {weather_description}, Time: {time_getting}")
        save_weather_data.delay(city_name, country, temperature, humidity, weather_description, time_getting)
    else:
        print("Could not retrieve weather conditions.")
else:
    print("Could not retrieve weather data.")
