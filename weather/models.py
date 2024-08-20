from django.db import models
from users.models import CustomUser


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}, {self.country}'


class Weather(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather')
    temperature = models.FloatField()
    humidity = models.FloatField()
    weather_description = models.TextField()
    time_getting = models.DateTimeField()

    def __str__(self):
        return f"Weather in {self.city.name} on {self.time_getting}"


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_subscriptions')
    notification_period = models.IntegerField(choices=[(1, '1 hour'), (3, '3 hours'), (6, '6 hours'), (12, '12 hours')],
                                              default=1)
    subscription_date = models.DateTimeField(auto_now_add=True)
    last_notified = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Subscription of {self.user.email} to {self.city.name}"
