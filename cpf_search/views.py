from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cpf
from .serializers import CpfSerializer
import json
from django.db.models import Q


def index(request):
    """Main page for CPF search"""
    return render(request, 'cpf_search/index.html')


def server_control(request):
    """Server control panel (replacement for PyQt GUI)"""
    return render(request, 'cpf_search/server_control.html')


import concurrent.futures
from django.db import connections

# ... (rest of your imports)

@api_view(['POST'])
def search_cpf(request):
    """API endpoint to search CPF data (replacement for socket server)"""
    try:
        # Extract search parameters from request
        name = request.data.get('name', '').strip()
        cpf = request.data.get('cpf', '').strip()
        date = request.data.get('birthdate', '').strip()
        request_id = request.data.get('request_id', 1)
        
        # Build query conditions
        conditions = Q()
        
        if name:
            conditions &= Q(nome__icontains=name)
        
        if cpf:
            # Clean CPF (remove dots and dashes)
            clean_cpf = cpf.replace('.', '').replace('-', '')
            conditions &= Q(cpf__exact=clean_cpf)
        
        if date:
            conditions &= Q(nasc__exact=date)
        
        # Function to execute the database query in a separate thread
        def execute_query():
            # Ensure a fresh connection for this thread
            connections.close_all()
            return list(Cpf.objects.filter(conditions)[:1000])

        # Execute query in a thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(execute_query)
            results = future.result()
        
        # Serialize results
        serializer = CpfSerializer(results, many=True)
        
        # Format response similar to original format
        response_data = {
            'response_id': request_id,
            'user_data': [{
                'name': item['nome'],
                'cpf': item['cpf'],
                'date': str(item['nasc']) if item['nasc'] else ''
            } for item in serializer.data]
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
