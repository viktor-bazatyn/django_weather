from datetime import datetime

import requests
from dotenv import dotenv_values
from pathlib import Path

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
            return latitude, longitude
        else:
            print('No weather data in the city')
            return None, None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None, None


def get_weather_conditions(latitude, longitude):
    API_URL = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric'
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()
        if data:
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            weather = data['weather'][0]['description']
            time_getting = datetime.now()
            return temperature, humidity, weather, time_getting
        else:
            print('No weather data available.')
            return None, None, None, None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None, None, None, None


city_name = input('Enter city name: ')
lat, lon = get_weather_coordinates(city_name)
if lat is not None and lon is not None:
    temp, humidity, weather_desc, time_getting = get_weather_conditions(lat, lon)
    if temp is not None:
        print(f"Temperature: {temp}°C, Humidity: {humidity}%, Weather: {weather_desc}, Time: {time_getting}")
else:
    print("Could not retrieve weather data.")
