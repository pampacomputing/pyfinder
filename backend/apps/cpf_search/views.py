from db_utils import get_cnpj_db_connection
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cpf
from project.serializers import CpfSerializer
from django.db.models import Q
from django.conf import settings
import re


from django.db import connections


from unidecode import unidecode


@api_view(["GET", "POST"])
def search_cpf(request):
    try:
        # Extract search parameters from request
        name = (
            request.data.get("name", "").strip()
            if request.method == "POST"
            else request.GET.get("name", "").strip()
        )
        cpf = (
            request.data.get("cpf", "").strip()
            if request.method == "POST"
            else request.GET.get("cpf", "").strip()
        )
        request_id = (
            request.data.get("request_id", 1)
            if request.method == "POST"
            else request.GET.get("request_id", 1)
        )

        response_data = {
            "response_id": request_id,
            "user_data": [],
        }

        if cpf or name:
            cpf_conditions = Q()
            if cpf:
                clean_cpf = cpf.replace(".", "").replace("-", "")
                cpf_conditions &= Q(cpf__exact=clean_cpf)
            if name:
                # Normalize name using unidecode
                normalized_name = unidecode(name.upper())
                for word in normalized_name.split():
                    cpf_conditions &= Q(nome__icontains=word)

            def execute_cpf_query():
                return list(Cpf.objects.using('basecpf_db').filter(cpf_conditions)[:1000])

            cpf_results = execute_cpf_query()

            cpf_serializer = CpfSerializer(cpf_results, many=True)

            for cpf_item in cpf_serializer.data:
                # Gender mapping
                gender = "Unknown"
                if cpf_item.get("sexo") == "M":
                    gender = "Male"
                elif cpf_item.get("sexo") == "F":
                    gender = "Female"

                person_data = {
                    "name": cpf_item.get("nome"),
                    "cpf": cpf_item["cpf"],
                    "date": str(cpf_item["nasc"]) if cpf_item["nasc"] else "",
                    "gender": gender,
                }
                response_data["user_data"].append(person_data)

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_companies_by_name(request):
    person_name = request.GET.get("name", "").strip()
    person_cpf = request.GET.get("cpf", "").strip()

    if not person_name or not person_cpf:
        return Response(
            {"error": "Name and CPF are required."}, status=status.HTTP_400_BAD_REQUEST
        )

    clean_cpf = re.sub(r"\D", "", person_cpf)
    if len(clean_cpf) != 11:
        return Response(
            {"error": "Invalid CPF format."}, status=status.HTTP_400_BAD_REQUEST
        )
    masked_cpf = f"***{clean_cpf[3:9]}**"

    def execute_query_and_process_data():
        conn = None
        try:
            conn = get_cnpj_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    s.cnpj,
                    e.razao_social,
                    e.natureza_juridica,
                    e.porte_empresa,
                    e.capital_social,
                    est.nome_fantasia,
                    est.situacao_cadastral,
                    est.data_situacao_cadastral,
                    est.motivo_situacao_cadastral,
                    est.logradouro,
                    est.numero,
                    est.complemento,
                    est.bairro,
                    est.cep,
                    est.uf,
                    m.descricao as municipio
                FROM socios s
                JOIN empresas e ON s.cnpj_basico = e.cnpj_basico
                JOIN estabelecimento est ON s.cnpj_basico = est.cnpj_basico
                LEFT JOIN municipio m ON est.municipio = m.codigo
                WHERE s.nome_socio = ? AND s.cnpj_cpf_socio = ? AND est.matriz_filial = '1'
            """,
                (person_name, masked_cpf),
            )
            company_details = cursor.fetchall()

            if not company_details:
                return []

            def get_description(table_name, code):
                if code is None or not code.strip():
                    return None
                cursor.execute(
                    f"SELECT descricao FROM {table_name} WHERE codigo = ?", (code,)
                )
                result = cursor.fetchone()
                return result["descricao"] if result else None

            porte_mapping = {
                "01": "MICRO EMPRESA",
                "03": "EMPRESA DE PEQUENO PORTE",
                "05": "DEMAIS",
            }

            associated_companies = []
            for company_row in company_details:
                company = dict(company_row)
                situacao_cadastral_desc = get_description(
                    "motivo", company["situacao_cadastral"]
                )
                motivo_situacao_desc = get_description(
                    "motivo", company["motivo_situacao_cadastral"]
                )
                natureza_juridica_desc = get_description(
                    "natureza_juridica", company["natureza_juridica"]
                )
                porte_desc = porte_mapping.get(company["porte_empresa"], "NAO INFORMADO")

                associated_companies.append(
                    {
                        "cnpj": company["cnpj"],
                        "razao_social": company["razao_social"],
                        "nome_fantasia": company["nome_fantasia"],
                        "natureza_juridica": natureza_juridica_desc,
                        "porte": porte_desc,
                        "capital_social": company["capital_social"],
                        "situacao_cadastral": situacao_cadastral_desc,
                        "data_situacao_cadastral": company["data_situacao_cadastral"],
                        "motivo_situacao_cadastral": motivo_situacao_desc,
                        "endereco": {
                            "logradouro": company["logradouro"],
                            "numero": company["numero"],
                            "complemento": company["complemento"],
                            "bairro": company["bairro"],
                            "municipio": company["municipio"],
                            "uf": company["uf"],
                            "cep": company["cep"],
                        }
                    }
                )
            return associated_companies
        finally:
            if conn:
                conn.close()

    try:
        associated_companies = execute_query_and_process_data()

        return Response(
            {"associated_companies": associated_companies}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
