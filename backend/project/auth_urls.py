from django.urls import path
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny

urlpatterns = [
    path(
        "registration/",
        RegisterView.as_view(permission_classes=[AllowAny], authentication_classes=[]),
        name="rest_register",
    ),
    path(
        "login/",
        LoginView.as_view(permission_classes=[AllowAny], authentication_classes=[]),
        name="rest_login",
    ),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
]
