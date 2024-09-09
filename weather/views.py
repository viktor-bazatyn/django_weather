from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def create_subscription(request):

    return render(request, 'create_subscription.html')


def view_subscriptions(request):

    return render(request, 'view_subscriptions.html')


def settings(request):

    return render(request, 'settings.html')
