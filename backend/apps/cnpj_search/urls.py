from django.urls import path
from . import views

urlpatterns = [
    path("search/", views.CNPJSearchView.as_view(), name="search"),
]
