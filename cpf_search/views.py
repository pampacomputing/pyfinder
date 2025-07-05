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
        cnpj = request.data.get('cnpj', '').strip()
        date = request.data.get('birthdate', '').strip()
        request_id = request.data.get('request_id', 1)
        
        response_data = {
            'response_id': request_id,
            'user_data': [],
            'company_data': [],
            'partner_data': []
        }

        if cpf:
            clean_cpf = cpf.replace('.', '').replace('-', '')
            cpf_conditions = Q(cpf__exact=clean_cpf)
            if name:
                cpf_conditions &= Q(nome__icontains=name)
            if date:
                cpf_conditions &= Q(nasc__exact=date)

            def execute_cpf_query():
                connections.close_all()
                return list(Cpf.objects.filter(cpf_conditions)[:1000])

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_cpf_query)
                cpf_results = future.result()
            
            cpf_serializer = CpfSerializer(cpf_results, many=True)
            response_data['user_data'] = [{
                'name': item['nome'],
                'cpf': item['cpf'],
                'date': str(item['nasc']) if item['nasc'] else ''
            } for item in cpf_serializer.data]

        if cnpj:
            clean_cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
            
            def execute_cnpj_query():
                connections.close_all()
                return list(Empresas.objects.using('cnpj_db').filter(cnpj__exact=clean_cnpj)[:1000])

            def execute_socios_query():
                connections.close_all()
                return list(Socios.objects.using('cnpj_db').filter(cnpj_basico__exact=clean_cnpj[:8])[:1000])

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                cnpj_future = executor.submit(execute_cnpj_query)
                socios_future = executor.submit(execute_socios_query)
                
                cnpj_results = cnpj_future.result()
                socios_results = socios_future.result()

            response_data['company_data'] = [{
                'cnpj': item.cnpj,
                'razao_social': item.razao_social,
                'nome_fantasia': item.nome_fantasia,
                'situacao_cadastral': item.situacao_cadastral,
                'data_situacao_cadastral': item.data_situacao_cadastral,
                'motivo_situacao_cadastral': item.motivo_situacao_cadastral,
                'cod_nat_juridica': item.cod_nat_juridica,
                'data_inicio_ativ': item.data_inicio_ativ,
                'cnae_fiscal': item.cnae_fiscal,
                'tipo_logradouro': item.tipo_logradouro,
                'logradouro': item.logradouro,
                'numero': item.numero,
                'complemento': item.complemento,
                'bairro': item.bairro,
                'cep': item.cep,
                'uf': item.uf,
                'cod_municipio': item.cod_municipio,
                'municipio': item.municipio,
                'ddd_1': item.ddd_1,
                'telefone_1': item.telefone_1,
                'ddd_2': item.ddd_2,
                'telefone_2': item.telefone_2,
                'ddd_fax': item.ddd_fax,
                'fax': item.fax,
                'email': item.email,
                'qualif_resp': item.qualif_resp,
                'capital_social': item.capital_social,
                'porte': item.porte,
                'opc_simples': item.opc_simples,
                'data_opc_simples': item.data_opc_simples,
                'data_exc_simples': item.data_exc_simples,
                'opc_mei': item.opc_mei,
                'situacao_especial': item.situacao_especial,
                'data_sit_especial': item.data_sit_especial,
            } for item in cnpj_results]

            response_data['partner_data'] = [{
                'cnpj_basico': item.cnpj_basico,
                'id_socio': item.id_socio,
                'nome_socio': item.nome_socio,
                'cpf_cnpj_socio': item.cpf_cnpj_socio,
                'cod_qualif_socio': item.cod_qualif_socio,
                'data_entrada_sociedade': item.data_entrada_sociedade,
                'pais': item.pais,
                'repr_legal': item.repr_legal,
                'nome_repr': item.nome_repr,
                'cod_qualif_repr_legal': item.cod_qualif_repr_legal,
                'faixa_etaria': item.faixa_etaria,
            } for item in socios_results]
        
        # Data correlation (if both CPF and CNPJ are provided)
        if cpf and cnpj:
            # Example: Find if any CPF search result is a partner in the CNPJ search result
            # This is a basic example; real correlation might be more complex
            correlated_data = []
            cpf_numbers_in_results = {item['cpf'] for item in response_data['user_data']}
            for partner in response_data['partner_data']:
                if partner['cpf_cnpj_socio'] in cpf_numbers_in_results:
                    correlated_data.append({
                        'cpf_info': next(item for item in response_data['user_data'] if item['cpf'] == partner['cpf_cnpj_socio']),
                        'partner_info': partner
                    })
            response_data['correlated_data'] = correlated_data
        
        return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
