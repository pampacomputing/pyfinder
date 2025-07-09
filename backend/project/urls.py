from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.cpf_search.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("accounts/", include("allauth.urls")),
    path("api/cnpj/", include("apps.cnpj_search.urls")),
    path("", TemplateView.as_view(template_name="index.html")),
]
