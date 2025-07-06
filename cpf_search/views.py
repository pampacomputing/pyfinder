from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cpf
from .serializers import CpfSerializer
from .cnpj_models import Empresas, Socios # Import Empresas and Socios
import json
from django.db.models import Q

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
        cnpj = request.data.get('cnpj', '').strip() if request.method == 'POST' else request.GET.get('cnpj', '').strip()
        # Removed date = request.data.get('birthdate', '').strip() if request.method == 'POST' else request.GET.get('birthdate', '').strip()
        request_id = request.data.get('request_id', 1) if request.method == 'POST' else request.GET.get('request_id', 1)

        response_data = {
            'response_id': request_id,
            'user_data': [],
            'company_data': {},
            'partners_data': []
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
                person_data = {
                    'name': cpf_item['nome'],
                    'cpf': cpf_item['cpf'],
                    'date': str(cpf_item['nasc']) if cpf_item['nasc'] else '',
                    'associated_companies': []
                }

                # Search for companies where this CPF is a partner
                clean_cpf_partner = cpf_item['cpf'].replace('.', '').replace('-', '')
                socios_as_partner = Socios.objects.using('cnpj_db').filter(cnpj_cpf_socio__exact=clean_cpf_partner).values('cnpj_basico').distinct()

                for socio_entry in socios_as_partner:
                    cnpj_basico = socio_entry['cnpj_basico']

                    # Get company details
                    company_details = Empresas.objects.using('cnpj_db').filter(cnpj_basico__exact=cnpj_basico).values(
                        'cnpj_basico',
                        'razao_social',
                        'natureza_juridica',
                        'qualificacao_responsavel',
                        'porte_empresa',
                        'ente_federativo_responsavel',
                        'capital_social'
                    ).first() # Use .first() as we expect only one company per cnpj_basico

                    if company_details:
                        company_partners = []
                        # Get all partners for this company
                        all_socios_for_company = Socios.objects.using('cnpj_db').filter(cnpj_basico__exact=cnpj_basico).values(
                            'cnpj',
                            'cnpj_basico',
                            'identificador_de_socio',
                            'nome_socio',
                            'cnpj_cpf_socio',
                            'qualificacao_socio',
                            'data_entrada_sociedade',
                            'pais',
                            'representante_legal',
                            'nome_representante',
                            'qualificacao_representante_legal',
                            'faixa_etaria'
                        )

                        for partner in all_socios_for_company:
                            cpf_info = None
                            if partner['cnpj_cpf_socio']:
                                try:
                                    cpf_obj = Cpf.objects.get(cpf=partner['cnpj_cpf_socio'])
                                    cpf_info = {
                                        'nome': cpf_obj.nome,
                                        'data_nascimento': str(cpf_obj.nasc) if cpf_obj.nasc else None,
                                        'genero': None # Gender is not in Cpf model, so setting to None
                                    }
                                except Cpf.DoesNotExist:
                                    pass # CPF not found in basecpf.db, continue without enriching

                            company_partners.append({
                                'cpf': partner['cnpj_cpf_socio'],
                                'nome': cpf_info['nome'] if cpf_info else partner['nome_socio'], # Use enriched name if available
                                'data_nascimento': cpf_info['data_nascimento'] if cpf_info else None,
                                'genero': cpf_info['genero'] if cpf_info else None,
                                'cnpj': partner['cnpj'],
                                'cnpj_basico': partner['cnpj_basico'],
                                'identificador_de_socio': partner['identificador_de_socio'],
                                'qualificacao_socio': partner['qualificacao_socio'],
                                'data_entrada_sociedade': partner['data_entrada_sociedade'],
                                'pais': partner['pais'],
                                'representante_legal': partner['representante_legal'],
                                'nome_representante': partner['nome_representante'],
                                'qualificacao_representante_legal': partner['qualificacao_representante_legal'],
                                'faixa_etaria': partner['faixa_etaria'],
                            })
                        
                        person_data['associated_companies'].append({
                            'company_details': company_details,
                            'partners': company_partners
                        })
                response_data['user_data'].append(person_data)

        elif cnpj:
            clean_cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
            
            def execute_cnpj_query():
                connections.close_all()
                return list(Empresas.objects.using('cnpj_db').filter(cnpj_basico__exact=clean_cnpj).values(
                    'cnpj_basico',
                    'razao_social',
                    'natureza_juridica',
                    'qualificacao_responsavel',
                    'porte_empresa',
                    'ente_federativo_responsavel',
                    'capital_social'
                )[:1]) # Limit to 1 company

            def execute_socios_query():
                connections.close_all()
                return list(Socios.objects.using('cnpj_db').filter(cnpj_basico__exact=clean_cnpj[:8]).values(
                    'cnpj',
                    'cnpj_basico',
                    'identificador_de_socio',
                    'nome_socio',
                    'cnpj_cpf_socio',
                    'qualificacao_socio',
                    'data_entrada_sociedade',
                    'pais',
                    'representante_legal',
                    'nome_representante',
                    'qualificacao_representante_legal',
                    'faixa_etaria'
                )[:1000])

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                cnpj_future = executor.submit(execute_cnpj_query)
                socios_future = executor.submit(execute_socios_query)
                
                cnpj_results = cnpj_future.result()
                socios_results = socios_future.result()

            if cnpj_results:
                company = cnpj_results[0]
                response_data['company_data'] = {
                    'cnpj_basico': company['cnpj_basico'],
                    'razao_social': company['razao_social'],
                    'natureza_juridica': company['natureza_juridica'],
                    'qualificacao_responsavel': company['qualificacao_responsavel'],
                    'porte_empresa': company['porte_empresa'],
                    'ente_federativo_responsavel': company['ente_federativo_responsavel'],
                    'capital_social': company['capital_social'],
                }
            
            partners_data = []
            for partner in socios_results:
                cpf_info = None
                if partner['cnpj_cpf_socio']:
                    try:
                        cpf_obj = Cpf.objects.get(cpf=partner['cnpj_cpf_socio'])
                        cpf_info = {
                            'nome': cpf_obj.nome,
                            'data_nascimento': str(cpf_obj.nasc) if cpf_obj.nasc else None,
                            'genero': None # Gender is not in Cpf model, so setting to None
                        }
                    except Cpf.DoesNotExist:
                        pass # CPF not found in basecpf.db, continue without enriching

                partners_data.append({
                    'cpf': partner['cnpj_cpf_socio'],
                    'nome': cpf_info['nome'] if cpf_info else partner['nome_socio'], # Use enriched name if available
                    'data_nascimento': cpf_info['data_nascimento'] if cpf_info else None,
                    'genero': cpf_info['genero'] if cpf_info else None,
                    'cnpj': partner['cnpj'],
                    'cnpj_basico': partner['cnpj_basico']
                })
            response_data['partners_data'] = partners_data
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )