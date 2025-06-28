from django.urls import path
from . import views

app_name = 'cpf_search'

urlpatterns = [
    path('', views.index, name='index'),
    path('server/', views.server_control, name='server_control'),
    path('search/', views.search_cpf, name='search_cpf'),
]
