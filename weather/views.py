from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def create_subscription(request):
    # Логіка для створення підписки
    return render(request, 'create_subscription.html')


def view_subscriptions(request):
    # Логіка для перегляду підписок
    return render(request, 'view_subscriptions.html')


def settings(request):
    # Логіка для налаштувань
    return render(request, 'settings.html')
