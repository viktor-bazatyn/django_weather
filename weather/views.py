from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from weather.models import Subscription
from weather.forms import SubscriptionForm


def home(request):
    return render(request, 'home.html')


@login_required
def create_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            return redirect('weather:view_subscriptions')
    else:
        form = SubscriptionForm()

    return render(request, 'create_subscription.html', {'form': form})


@login_required
def view_subscriptions(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'view_subscriptions.html', {'subscriptions': subscriptions})


def settings(request):
    return render(request, 'settings.html')


@login_required
def update_subscription(request, id):
    subscription = get_object_or_404(Subscription, id=id, user=request.user)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription)
        if form.is_valid():
            form.save()
            return redirect('weather:view_subscriptions')
    else:
        form = SubscriptionForm(instance=subscription)

    return render(request, 'update_subscription.html', {'form': form})


@login_required
def delete_subscription(request, id):
    subscription = get_object_or_404(Subscription, id=id, user=request.user)

    if request.method == 'POST':
        subscription.delete()
        return redirect('weather:view_subscriptions')

    return render(request, 'delete_subscription.html', {'subscription': subscription})


@login_required
def subscription_detail(request, id):
    subscription = get_object_or_404(Subscription, id=id, user=request.user)
    return render(request, 'subscription_detail.html', {'subscription': subscription})
