from django.urls import path
from . import views
from .views import SubscriptionCreate, SubscriptionList, SubscriptionDeleteCity, CityWeatherDetailApi, UpdateSubscription

app_name = 'weather'

urlpatterns = [
    path('', views.home, name='home'),
    path('settings/', views.settings, name='settings'),
    path('subscriptions/', views.view_subscriptions, name='view_subscriptions'),
    path('subscriptions/create/', views.create_subscription, name='create_subscription'),
    path('subscriptions/<int:id>/update/', views.update_subscription, name='update_subscription'),
    path('subscriptions/<int:id>/delete/', views.delete_subscription, name='delete_subscription'),
    path('subscriptions/<int:subscription_id>/', views.subscription_detail, name='subscription_detail'),
    path('api/v1/create_subscriptions/', SubscriptionCreate.as_view(), name='create-subscription'),
    path('api/v1/subscriptions/', SubscriptionList.as_view(), name='update-subscription'),
    path('api/v1/subscriptions/delete_city/', SubscriptionDeleteCity.as_view(), name='delete-subscription-city'),
    path('api/v1/weather/', CityWeatherDetailApi.as_view(), name='city-weather'),
    path('api/v1/subscriptions/update_city/', UpdateSubscription.as_view(), name='update-city'),
]
