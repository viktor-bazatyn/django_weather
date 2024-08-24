from weather.models import Weather, City
from celery import shared_task


@shared_task
def save_weather_data(city_name, country, temperature, humidity, weather_description, time_getting):
    try:

        city, created = City.objects.get_or_create(name=city_name, defaults={'country': country})
        if created:
            print(f'City {city_name} in {country} created successfully')
        else:
            if city.country != country:
                city.country = country
                city.save()
                print(f'City {city_name} updated with new country {country}.')

        weather_data = Weather(
            city=city,
            temperature=temperature,
            humidity=humidity,
            weather_description=weather_description,
            time_getting=time_getting
        )
        weather_data.save()
        print(f'Weather data for {city.name}, {city.country} saved successfully')
    except Exception as e:
        print(f"An error occurred while saving the weather data: {e}")
