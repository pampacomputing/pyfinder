import sqlite3
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re
from django.conf import settings
from db_utils import get_cnpj_db_connection, get_basecpf_db_connection


class CNPJSearchView(APIView):
    def post(self, request, *args, **kwargs):
        cnpj = request.data.get("cnpj")

        if not cnpj:
            return Response(
                {"error": "CNPJ is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Input & formatting (backend re-validation)
        cnpj_digits = re.sub(r"[^0-9]", "", cnpj)
        if len(cnpj_digits) != 14:
            return Response(
                {"error": "CNPJ must have 14 digits."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Check-digit validation (backend re-validation)
        if not self._validate_cnpj_check_digits(cnpj_digits):
            return Response(
                {"error": "Invalid CNPJ check digits."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2.2. Normalize for lookup
        cnpj_basico = cnpj_digits[0:8]
        cnpj_ordem = cnpj_digits[8:12]
        cnpj_dv = cnpj_digits[12:14]

        cnpj_conn = get_cnpj_db_connection()
        cnpj_cursor = cnpj_conn.cursor()

        try:
            empresa_data = self._query_empresa(cnpj_cursor, cnpj_basico)
            if not empresa_data:
                return Response(
                    {"error": "CNPJ not found."}, status=status.HTTP_404_NOT_FOUND
                )

            estabelecimento_data = self._query_estabelecimento(
                cnpj_cursor, cnpj_basico, cnpj_ordem, cnpj_dv
            )
            simples_data = self._query_simples(cnpj_cursor, cnpj_basico)
            socios_data = self._query_socios(cnpj_cursor, cnpj_basico)

            enriched_empresa = self._enrich_empresa_data(
                cnpj_cursor, empresa_data
            )
            enriched_estabelecimento = self._enrich_estabelecimento_data(
                cnpj_cursor, estabelecimento_data
            )
            enriched_simples = self._enrich_simples_data(simples_data)

            basecpf_conn = get_basecpf_db_connection()
            basecpf_cursor = basecpf_conn.cursor()
            try:
                enriched_socios = self._enrich_socios_data_optimized(
                    basecpf_cursor, cnpj_cursor, socios_data
                )
            finally:
                basecpf_conn.close()


            response_data = self._assemble_json(
                cnpj_digits,
                enriched_empresa,
                enriched_estabelecimento,
                enriched_simples,
                enriched_socios,
            )

            return Response(response_data, status=status.HTTP_200_OK)

        finally:
            cnpj_conn.close()

    def _validate_cnpj_check_digits(self, cnpj):
        def calculate_dv(cnpj_part, weights):
            total = 0
            for i, digit in enumerate(cnpj_part):
                total += int(digit) * weights[i]
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        # Calculate first check digit
        cnpj_12_digits = cnpj[0:12]
        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        dv1_calculated = calculate_dv(cnpj_12_digits, weights1)

        # Validate first check digit
        if int(cnpj[12]) != dv1_calculated:
            return False

        # Calculate second check digit
        cnpj_13_digits = cnpj[0:13]  # Includes the first calculated DV
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        dv2_calculated = calculate_dv(cnpj_13_digits, weights2)

        # Validate second check digit
        if int(cnpj[13]) != dv2_calculated:
            return False

        return True

    def _query_empresa(self, cursor, cnpj_basico):
        cursor.execute(
            """
            SELECT
                razao_social, natureza_juridica, qualificacao_responsavel,
                porte_empresa, ente_federativo_responsavel, capital_social
            FROM empresas
            WHERE cnpj_basico = ?;
        """,
            (cnpj_basico,),
        )
        return cursor.fetchone()

    def _query_estabelecimento(self, cursor, cnpj_basico, cnpj_ordem, cnpj_dv):
        cursor.execute(
            """
            SELECT
                cnpj_ordem, cnpj_dv, matriz_filial, nome_fantasia,
                situacao_cadastral, data_situacao_cadastral,
                motivo_situacao_cadastral, nome_cidade_exterior,
                pais, data_inicio_atividades, cnae_fiscal,
                cnae_fiscal_secundaria, tipo_logradouro,
                logradouro, numero, complemento, bairro, cep,
                uf, municipio, ddd1, telefone1, ddd2, telefone2,
                ddd_fax, fax, correio_eletronico,
                situacao_especial, data_situacao_especial
            FROM estabelecimento
            WHERE cnpj_basico = ?
              AND cnpj_ordem = ?
              AND cnpj_dv    = ?;
        """,
            (cnpj_basico, cnpj_ordem, cnpj_dv),
        )
        return cursor.fetchone()

    def _query_simples(self, cursor, cnpj_basico):
        cursor.execute(
            """
            SELECT
                opcao_simples, data_opcao_simples, data_exclusao_simples,
                opcao_mei, data_opcao_mei, data_exclusao_mei
            FROM simples
            WHERE cnpj_basico = ?;
        """,
            (cnpj_basico,),
        )
        return cursor.fetchone()

    def _query_socios(self, cursor, cnpj_basico):
        cursor.execute(
            """
            SELECT
                nome_socio, cnpj_cpf_socio, qualificacao_socio,
                data_entrada_sociedade, pais, representante_legal,
                nome_representante, qualificacao_representante_legal,
                faixa_etaria
            FROM socios
            WHERE cnpj_basico = ?;
        """,
            (cnpj_basico,),
        )
        return cursor.fetchall()

    def _get_description(self, cursor, table_name, code):
        if code is None:
            return None
        cursor.execute(
            f"""
            SELECT descricao
            FROM {table_name}
            WHERE codigo = ?;
        """,
            (code,),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def _get_descriptions_in_batch(self, cursor, table_name, codes):
        if not codes:
            return {}
        
        unique_codes = list(set(codes))
        
        query = f"""
            SELECT codigo, descricao
            FROM {table_name}
            WHERE codigo IN ({','.join(['?'] * len(unique_codes))})
        """
        cursor.execute(query, unique_codes)
        
        return {row[0]: row[1] for row in cursor.fetchall()}

    def _enrich_empresa_data(self, cursor, data):
        if not data:
            return {}

        codes_to_fetch = {
            "natureza_juridica": [data[1]],
            "qualificacao_socio": [data[2]]
        }

        descriptions = {
            table: self._get_descriptions_in_batch(cursor, table, codes)
            for table, codes in codes_to_fetch.items()
        }

        porte_mapping = {
            "01": "MICRO EMPRESA",
            "03": "EMPRESA DE PEQUENO PORTE",
            "05": "DEMAIS",
        }
        porte_descricao = porte_mapping.get(data[3], "NAO INFORMADO")

        return {
            "razao_social": data[0],
            "natureza_juridica": {
                "codigo": data[1],
                "descricao": descriptions.get("natureza_juridica", {}).get(data[1]),
            },
            "qualificacao_responsavel": {
                "codigo": data[2],
                "descricao": descriptions.get("qualificacao_socio", {}).get(data[2]),
            },
            "porte": porte_descricao,
            "ente_federativo_responsavel": data[4],
            "capital_social": data[5],
        }

    def _enrich_estabelecimento_data(self, cursor, data):
        if not data:
            return {}

        cnae_codes = [data[10]]
        if data[11]:
            cnae_codes.extend([c.strip() for c in data[11].split(",")])

        codes_to_fetch = {
            "motivo": [data[4], data[6]],
            "pais": [data[8]],
            "cnae": cnae_codes,
            "municipio": [data[19]],
        }

        descriptions = {
            table: self._get_descriptions_in_batch(cursor, table, codes)
            for table, codes in codes_to_fetch.items()
        }

        cnae_fiscal_secundaria = []
        if data[11]:  # cnae_fiscal_secundaria
            for cnae_code in data[11].split(","):
                cnae_code = cnae_code.strip()
                cnae_fiscal_secundaria.append(
                    {
                        "codigo": cnae_code,
                        "descricao": descriptions.get("cnae", {}).get(cnae_code),
                    }
                )

        return {
            "cnpj_ordem": data[0],
            "cnpj_dv": data[1],
            "matriz_filial": "MATRIZ" if data[2] == "1" else "FILIAL",
            "nome_fantasia": data[3],
            "situacao_cadastral": {
                "codigo": data[4],
                "descricao": descriptions.get("motivo", {}).get(data[4]),
            },
            "data_situacao_cadastral": data[5],
            "motivo_situacao_cadastral": {
                "codigo": data[6],
                "descricao": descriptions.get("motivo", {}).get(data[6]),
            },
            "nome_cidade_exterior": data[7],
            "pais": {
                "codigo": data[8],
                "descricao": descriptions.get("pais", {}).get(data[8]),
            },
            "data_inicio_atividades": data[9],
            "cnae_principal": {
                "codigo": data[10],
                "descricao": descriptions.get("cnae", {}).get(data[10]),
            },
            "cnae_secundarias": cnae_fiscal_secundaria,
            "tipo_logradouro": data[12],
            "logradouro": data[13],
            "numero": data[14],
            "complemento": data[15],
            "bairro": data[16],
            "cep": data[17],
            "uf": data[18],
            "municipio": {
                "codigo": data[19],
                "descricao": descriptions.get("municipio", {}).get(data[19]),
            },
            "ddd1": data[20],
            "telefone1": data[21],
            "ddd2": data[22],
            "telefone2": data[23],
            "ddd_fax": data[24],
            "fax": data[25],
            "correio_eletronico": data[26],
            "situacao_especial": data[27],
            "data_situacao_especial": data[28],
        }

    def _enrich_simples_data(self, data):
        if not data:
            return {}
        return {
            "opcao_simples": bool(data[0]),
            "data_opcao_simples": data[1],
            "data_exclusao_simples": data[2],
            "opcao_mei": bool(data[3]),
            "data_opcao_mei": data[4],
            "data_exclusao_mei": data[5],
        }

    def _enrich_socios_data_optimized(self, basecpf_cursor, cnpj_cursor, socios_data):
        if not socios_data:
            return []

        # Step 1: Collect all unique partner names
        partner_names = list(set([socio[0] for socio in socios_data]))

        # Step 2: Fetch all potential CPF matches for these names in one query
        query = f"""
            SELECT cpf, sexo, nasc, nome
            FROM cpf
            WHERE nome IN ({','.join(['?'] * len(partner_names))})
        """
        basecpf_cursor.execute(query, partner_names)
        potential_matches = basecpf_cursor.fetchall()

        # Step 3: Organize potential matches by name for quick lookup
        matches_by_name = {}
        for match in potential_matches:
            name = match[3]
            if name not in matches_by_name:
                matches_by_name[name] = []
            matches_by_name[name].append(match)

        # Step 4: Process partners, matching them with the fetched data in memory
        enriched_socios = []
        for socio in socios_data:
            nome_socio = socio[0]
            cnpj_cpf_socio_masked = socio[1]
            cpf_value, sexo, data_nascimento = None, None, None

            # Find the correct partner from the in-memory list
            if nome_socio in matches_by_name:
                for potential_match in matches_by_name[nome_socio]:
                    full_cpf = potential_match[0]
                    if self._mask_cpf(full_cpf) == cnpj_cpf_socio_masked:
                        cpf_value = full_cpf
                        sexo = potential_match[1]
                        data_nascimento = potential_match[2]
                        break  # Found the correct person

            enriched_socios.append(
                {
                    "cpf": cpf_value,
                    "nome": nome_socio,
                    "sexo": sexo,
                    "data_nascimento": data_nascimento,
                    "qualificacao_socio": {
                        "codigo": socio[2],
                        "descricao": self._get_description(
                            cnpj_cursor, "qualificacao_socio", socio[2]
                        ),
                    },
                    "data_entrada_sociedade": socio[3],
                    "pais": {
                        "codigo": socio[4],
                        "descricao": self._get_description(
                            cnpj_cursor, "pais", socio[4]
                        ),
                    },
                    "representante_legal": socio[5],
                    "nome_representante": socio[6],
                    "qualificacao_representante_legal": {
                        "codigo": socio[7],
                        "descricao": self._get_description(
                            cnpj_cursor, "qualificacao_socio", socio[7]
                        ),
                    },
                    "faixa_etaria": socio[8],
                }
            )
        return enriched_socios

    def _mask_cpf(self, cpf):
        """Masks a CPF string according to the rule: ***...**"""
        if not cpf or not isinstance(cpf, str):
            return ""
        cpf_digits = re.sub(r"\D", "", cpf)
        if len(cpf_digits) != 11:
            return ""
        return f"***{cpf_digits[3:9]}**"

    

    def _assemble_json(self, cnpj_digits, empresa, estabelecimento, simples, socios):
        # Mapping for porte_empresa is now handled in _enrich_empresa_data
        # Mapping for situacao_cadastral is now handled in _enrich_estabelecimento_data

        return {
            "cnpj": cnpj_digits,
            "empresa": {
                "razao_social": empresa.get("razao_social"),
                "nome_fantasia": estabelecimento.get("nome_fantasia"),
                "natureza_juridica": empresa.get("natureza_juridica"),
                "porte": empresa.get("porte"),
                "capital_social": empresa.get("capital_social"),
                "data_inicio_atividades": estabelecimento.get("data_inicio_atividades"),
                "matriz_filial": estabelecimento.get("matriz_filial"),
                "simples": simples,
                "situacao_especial": estabelecimento.get("situacao_especial"),
                "data_situacao_especial": estabelecimento.get("data_situacao_especial"),
                "ente_federativo_responsavel": empresa.get("ente_federativo_responsavel"),
                "qualificacao_responsavel": empresa.get("qualificacao_responsavel"),
                "endereco": {
                    "tipo_logradouro": estabelecimento.get("tipo_logradouro"),
                    "logradouro": estabelecimento.get("logradouro"),
                    "numero": estabelecimento.get("numero"),
                    "complemento": estabelecimento.get("complemento"),
                    "bairro": estabelecimento.get("bairro"),
                    "cep": estabelecimento.get("cep"),
                    "uf": estabelecimento.get("uf"),
                    "municipio": estabelecimento.get("municipio"),
                    "pais": estabelecimento.get("pais"),
                    "nome_cidade_exterior": estabelecimento.get("nome_cidade_exterior"),
                },
                "atividades": {
                    "cnae_principal": estabelecimento.get("cnae_principal"),
                    "cnae_secundarias": estabelecimento.get("cnae_secundarias"),
                },
                "contato": {
                    "telefone1": f"{estabelecimento.get('ddd1')} {estabelecimento.get('telefone1')}"
                    if estabelecimento.get("ddd1") and estabelecimento.get("telefone1")
                    else None,
                    "telefone2": f"{estabelecimento.get('ddd2')} {estabelecimento.get('telefone2')}"
                    if estabelecimento.get("ddd2") and estabelecimento.get("telefone2")
                    else None,
                    "fax": f"{estabelecimento.get('ddd_fax')} {estabelecimento.get('fax')}"
                    if estabelecimento.get("ddd_fax") and estabelecimento.get("fax")
                    else None,
                    "email": estabelecimento.get("correio_eletronico"),
                },
                "situacao_cadastral": {
                    "codigo": estabelecimento.get("situacao_cadastral", {}).get(
                        "codigo"
                    ),
                    "descricao": estabelecimento.get("situacao_cadastral", {}).get(
                        "descricao"
                    ),
                    "data": estabelecimento.get("data_situacao_cadastral"),
                    "motivo": estabelecimento.get("motivo_situacao_cadastral"),
                },
            },
            "socios": socios,
        }