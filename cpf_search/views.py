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
    return render(request, 'cpf_search/index.html')

def server_control(request):
    return render(request, 'cpf_search/server_control.html')

@api_view(['GET', 'POST'])
def search_cpf(request):
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
    person_name = request.GET.get('name', '').strip()
    if not person_name:
        return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)

    cnpj_db_path = settings.DATABASES['cnpj_db']['NAME']
    associated_companies = []

    try:
        conn = sqlite3.connect(cnpj_db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # The socio's CNPJ is the full CNPJ, so we extract the basic part for joining.
        cursor.execute("""
            SELECT
                s.cnpj,
                e.razao_social,
                e.natureza_juridica,
                e.porte_empresa,
                e.capital_social,
                est.nome_fantasia,
                est.situacao_cadastral,
                est.data_situacao_cadastral,
                est.motivo_situacao_cadastral
            FROM socios s
            JOIN empresas e ON SUBSTR(s.cnpj, 1, 8) = e.cnpj_basico
            JOIN estabelecimento est ON SUBSTR(s.cnpj, 1, 8) = est.cnpj_basico
            WHERE s.nome_socio = ? AND est.matriz_filial = '1'
        """, (person_name,))
        
        company_details = cursor.fetchall()

        # Description lookups
        def get_description(table_name, code):
            if code is None or not code.strip():
                return None
            # Use a new cursor for lookups to not interfere with the main query
            lookup_cursor = conn.cursor()
            lookup_cursor.execute(f"SELECT descricao FROM {table_name} WHERE codigo = ?", (code,))
            result = lookup_cursor.fetchone()
            return result['descricao'] if result else None

        porte_mapping = {
            '01': 'MICRO EMPRESA',
            '03': 'EMPRESA DE PEQUENO PORTE',
            '05': 'DEMAIS'
        }

        for company_row in company_details:
            company = dict(company_row)
            
            situacao_cadastral_desc = get_description('motivo', company['situacao_cadastral'])
            motivo_situacao_desc = get_description('motivo', company['motivo_situacao_cadastral'])
            natureza_juridica_desc = get_description('natureza_juridica', company['natureza_juridica'])
            porte_desc = porte_mapping.get(company['porte_empresa'], 'NAO INFORMADO')

            associated_companies.append({
                'cnpj': company['cnpj'],
                'razao_social': company['razao_social'],
                'nome_fantasia': company['nome_fantasia'],
                'natureza_juridica': natureza_juridica_desc,
                'porte': porte_desc,
                'capital_social': company['capital_social'],
                'situacao_cadastral': situacao_cadastral_desc,
                'data_situacao_cadastral': company['data_situacao_cadastral'],
                'motivo_situacao_cadastral': motivo_situacao_desc
            })

    except sqlite3.Error as e:
        return Response({'error': f'Database error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        if conn:
            conn.close()

    return Response({'associated_companies': associated_companies}, status=status.HTTP_200_OK)
