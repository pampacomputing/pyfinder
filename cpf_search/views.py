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
import sqlite3
from django.conf import settings

import concurrent.futures
from django.db import connections

def index(request):
    """Main page for CPF search"""
    return render(request, 'cpf_search/index.html')

def server_control(request):
    """Server control panel (replacement for PyQt GUI)"""
    return render(request, 'cpf_search/server_control.html')

@api_view(['GET', 'POST'])
def search_cpf(request):
    """API endpoint to search CPF data (replacement for socket server)"""
    try:
        # Extract search parameters from request
        name = request.data.get('name', '').strip() if request.method == 'POST' else request.GET.get('name', '').strip()
        cpf = request.data.get('cpf', '').strip() if request.method == 'POST' else request.GET.get('cpf', '').strip()
        # Removed date = request.data.get('birthdate', '').strip() if request.method == 'POST' else request.GET.get('birthdate', '').strip()
        request_id = request.data.get('request_id', 1) if request.method == 'POST' else request.GET.get('request_id', 1)

        response_data = {
            'response_id': request_id,
            'user_data': [],
        }

        if cpf or name:
            cpf_conditions = Q()
            if cpf:
                clean_cpf = cpf.replace('.', '').replace('-', '')
                cpf_conditions &= Q(cpf__exact=clean_cpf)
            if name:
                for word in name.upper().split():
                    cpf_conditions &= Q(nome__icontains=word)

            def execute_cpf_query():
                connections.close_all()
                return list(Cpf.objects.filter(cpf_conditions)[:1000])

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_cpf_query)
                cpf_results = future.result()

            cpf_serializer = CpfSerializer(cpf_results, many=True)
            
            for cpf_item in cpf_serializer.data:
                # Gender mapping
                gender = 'Unknown'
                if cpf_item.get('sexo') == 'M':
                    gender = 'Male'
                elif cpf_item.get('sexo') == 'F':
                    gender = 'Female'

                person_data = {
                    'name': cpf_item.get('nome'),
                    'cpf': cpf_item['cpf'],
                    'date': str(cpf_item['nasc']) if cpf_item['nasc'] else '',
                    'gender': gender,
                }
                response_data['user_data'].append(person_data)

        
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_companies_by_name(request):
    """API endpoint to get companies associated with a person's name."""
    person_name = request.GET.get('name', '').strip()
    if not person_name:
        return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)

    cnpj_db_path = settings.DATABASES['cnpj_db']['NAME']
    associated_companies = []

    try:
        conn = sqlite3.connect(cnpj_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT s.cnpj, e.razao_social, e.capital_social
            FROM socios s
            JOIN empresas e ON s.cnpj_basico = e.cnpj_basico
            WHERE s.nome_socio = ?
        """, (person_name,))
        company_details = cursor.fetchall()

        for company in company_details:
            associated_companies.append({
                'cnpj': company[0],
                'razao_social': company[1],
                'capital_social': company[2]
            })
    except sqlite3.Error as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        if conn:
            conn.close()

    return Response({'associated_companies': associated_companies}, status=status.HTTP_200_OK)
