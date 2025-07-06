from django.urls import path
from .views import CNPJSearchView

urlpatterns = [
    path('search/', CNPJSearchView.as_view(), name='cnpj_search'),
]