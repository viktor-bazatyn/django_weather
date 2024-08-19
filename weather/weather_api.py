import requests
from dotenv import dotenv_values
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
config = dotenv_values(BASE_DIR / ".env")
API_KEY = config.get('OPENWEATHER_API_KEY')


def get_weather_coordinates(city_name):
    API_URL = f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={API_KEY}'
    response = requests.get(API_URL)

    if response.status_code == 200:
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


city = input('Enter city name: ')
lat, lon = get_weather_coordinates(city)
if lat is not None and lon is not None:
    print(f"Coordinates for {city}: Latitude = {lat}, Longitude = {lon}")
else:
    print("Coordinates not found.")
