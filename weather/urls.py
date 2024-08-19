from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
]
app_name = 'weather'

