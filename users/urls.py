from django.urls import path
from django.conf.urls import include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"),
         name="password_reset"),
    path("password_reset/done/",
         auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reseted.html"),
         name="password_reset_done"
         ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/my_custom_password_reset_confirm.html"),
        name="password_reset_confirm"
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/my_custom_password_reset_complete.html"),
        name="password_reset_complete"
    ),
    path("password_change/", auth_views.PasswordChangeView.as_view(template_name="registration/password_change.html"),
         name="password_change"),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration'
                                                                                          '/password_changed.html'),
         name='password_change_done'),
    path("logouts/", auth_views.LogoutView.as_view(next_page='weather:home'), name="logouts"),
]
