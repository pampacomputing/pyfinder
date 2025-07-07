from django.urls import path
from . import views

app_name = 'cpf_search'

urlpatterns = [
    path('', views.index, name='index'),
    path('server/', views.server_control, name='server_control'),
    path('search/', views.search_cpf, name='search_cpf'),
    path('get_companies_by_name/', views.get_companies_by_name, name='get_companies_by_name'),
]
