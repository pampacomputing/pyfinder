import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
from .models import Person


def search_view(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return HttpResponseBadRequest('Query parameter is required')

    results = []
    for alias in ('default', 'secondary'):
        qs = Person.objects.using(alias).filter(
            Q(name__icontains=query) |
            Q(cpf__icontains=query)
        )
        for person in qs:
            results.append({
                'name': person.name,
                'cpf': person.cpf,
                'gender': person.gender,
                'date': person.date,
                'database': alias
            })

    return JsonResponse({'results': results})
