from django.conf import settings
from django.http import JsonResponse
from django.db import connections
from django.views import View


class SearchView(View):
    def get(self, request):
        query = request.GET.get('query', '')
        if not query:
            return JsonResponse({'error': 'Query parameter is required.'}, status=400)

        results = []
        for alias in ('default', 'secondary'):
            cursor = connections[alias].cursor()
            cursor.execute(
                "SELECT name, cpf, gender, date FROM cpf WHERE name LIKE ? LIMIT 100",
                [f'%{query}%']
            )
            for row in cursor.fetchall():
                results.append({
                    'name': row[0],
                    'cpf': row[1],
                    'gender': row[2],
                    'date': row[3],
                })
        return JsonResponse({'results': results})
