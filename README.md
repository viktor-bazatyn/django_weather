# DjangoWeather

**DjangoWeather** is a Django-based web application that allows users to subscribe to periodic email updates 
with the current weather conditions for their chosen city.

## Key Features

- User registration and authentication
- City-based weather subscriptions
- Customizable notification frequency (in hours)
- Email notifications with up-to-date weather
- Integration with the OpenWeatherMap API
- Background task handling using Celery + Redis


## Technology Stack

- Python 3.11
- Django 5
- PostgreSQL
- Celery
- Redis
- Docker + Docker Compose
- django-celery-beat
- SMTP (for sending emails)

## Setup & Run

1. Clone the Repository

```git clone git@github.com:viktor-bazatyn/django_weather.git```

2. Create .env file

Create a .env file in the root of the project with the following content:
```
SECRET_KEY=your_secret_key
DEBUG=True

# OpenWeather API
OPENWEATHER_API_KEY=your_openweather_key

# PostgreSQL
POSTGRES_USER=my_user
POSTGRES_PASSWORD=my_secure_password
POSTGRES_DB=my_database
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis + Celery
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email
DEFAULT_FROM_EMAIL=your_email@example.com

# Allowed hosts
ALLOWED_HOST=127.0.0.1
```

3. Run Migrations

Before running the containers, make migrations locally:

```python manage.py makemigrations```

Then build and start the Docker containers:

```docker-compose up --build```

Once everything is up, apply the migrations inside the container:

```docker-compose exec web python manage.py migrate```

4. Run Celery & Beat

Open two terminals and run:

Celery Beat:

```docker-compose exec web celery -A base beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler```

Celery Worker:

```docker-compose exec web  celery -A base worker -l INFO ```

5. Manually Schedule the Weather Reminder Task

```angular2html
docker-compose exec web python manage.py shell
>>> from weather.tasks import schedule_weather_reminder
>>> schedule_weather_reminder()
```

📫 Email Notifications

Users choose a city and how often they'd like to receive updates (e.g., hourly).
Celery fetches weather data from the OpenWeatherMap API and sends it to the registered email address.