import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

from weather.tasks import get_weather_coordinates, get_weather_conditions, save_weather_data

city_name = input('Enter city name: ')


coordinates_result = get_weather_coordinates.delay(city_name)

coordinates = coordinates_result.get()

if coordinates and all(coordinates):
    lat, lon, country = coordinates
    weather_result = get_weather_conditions.delay(lat, lon)
    weather_data = weather_result.get()

    if weather_data and all(weather_data):
        temperature, humidity, weather_description, time_getting = weather_data
        save_weather_data.delay(city_name, country, temperature, humidity, weather_description, time_getting)
        print(
            f"Temperature: {temperature}°C, Humidity: {humidity}%, Weather: {weather_description}, Time: {time_getting}")
    else:
        print("Could not retrieve weather conditions")
else:
    print("Could not retrieve weather data")

