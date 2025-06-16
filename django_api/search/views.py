"""Views for search API."""

import json

from django.http import JsonResponse
from django.db import connections
from django.views import View

from .utils import User, execute_query


class SearchView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode())
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)

        request_id = payload.get("request_id", 0)
        data = payload.get("user_data", {})

        user = User(
            name=data.get("name", ""),
            cpf=data.get("cpf", ""),
            gender=data.get("gender", ""),
            date=data.get("date", ""),
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

        return JsonResponse({"response_id": request_id, "user_data": results})
