"""Views for search API."""

from django.http import JsonResponse
from django.db import connections
from django.views import View

from .utils import User, execute_query


class SearchView(View):
    def get(self, request):
        user = User(
            name=request.GET.get("name", ""),
            cpf=request.GET.get("cpf", ""),
            date=request.GET.get("date", ""),
        )

        if not any([user.name, user.cpf, user.date]):
            return JsonResponse(
                {"error": "At least one of name, cpf or date must be provided."},
                status=400,
            )

        results: list[dict] = []
        for alias in ("default", "secondary"):
            with connections[alias].cursor() as cursor:
                results.extend(execute_query(cursor, user))

        return JsonResponse({"results": results})
