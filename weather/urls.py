from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.home, name='home'),
    path('create-subscription/', views.create_subscription, name='create_subscription'),
    path('view-subscriptions/', views.view_subscriptions, name='view_subscriptions'),
    path('settings/', views.settings, name='settings'),
]


