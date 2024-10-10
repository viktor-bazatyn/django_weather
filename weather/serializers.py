from rest_framework import serializers
from weather.models import Subscription, City


class SubscriptionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.email', read_only=True)
    city_name_ = serializers.CharField(source='city.name', read_only=True)
    city_name = serializers.CharField(write_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user_name', 'city_name_', 'city_name', 'notification_period', 'subscription_date',
                  'last_notified']
        read_only_fields = ['user', 'subscription_date', 'last_notified']

    def create(self, validated_data):
        city_name = validated_data.pop('city_name')
        city, created = City.objects.get_or_create(name=city_name)
        subscription = Subscription.objects.create(city=city, **validated_data)
        return subscription