from django.urls import path
from . import views

app_name = 'cpf_search'

urlpatterns = [
    path('search/', views.search_cpf, name='search_cpf'),
    path('get_companies_by_name/', views.get_companies_by_name, name='get_companies_by_name'),
]
