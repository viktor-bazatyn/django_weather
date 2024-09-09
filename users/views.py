from django.contrib.auth import login
from django.shortcuts import redirect, render
from users.forms import CustomUserCreationForm
from users.models import CustomUser
from django.contrib import messages


# Create your views here.
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
                return render(request, "users/register.html", {"form": form})
            else:
                user = form.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('weather:home')
        else:
            return render(request, "users/register.html", {"form": form})
    else:
        form = CustomUserCreationForm()
        return render(request, "users/register.html", {"form": form})
