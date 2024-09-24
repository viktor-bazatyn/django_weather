from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.home, name='home'),
    path('settings/', views.settings, name='settings'),
    path('subscriptions/', views.view_subscriptions, name='view_subscriptions'),
    path('subscriptions/create/', views.create_subscription, name='create_subscription'),
    path('subscriptions/<int:id>/update/', views.update_subscription, name='update_subscription'),
    path('subscriptions/<int:id>/delete/', views.delete_subscription, name='delete_subscription'),
    path('subscriptions/<int:id>/', views.subscription_detail, name='subscription_detail'),
]
