import sqlite3
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re
from django.conf import settings
import threading

class CNPJSearchView(APIView):
    def post(self, request, *args, **kwargs):
        cnpj = request.data.get('cnpj')

        if not cnpj:
            return Response({"error": "CNPJ is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Input & formatting (backend re-validation)
        cnpj_digits = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj_digits) != 14:
            return Response({"error": "CNPJ must have 14 digits."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check-digit validation (backend re-validation)
        if not self._validate_cnpj_check_digits(cnpj_digits):
            return Response({"error": "Invalid CNPJ check digits."}, status=status.HTTP_400_BAD_REQUEST)

        # 2.2. Normalize for lookup
        cnpj_basico = cnpj_digits[0:8]
        cnpj_ordem = cnpj_digits[8:12]
        cnpj_dv = cnpj_digits[12:14]

        cnpj_db_path = settings.DATABASES['cnpj_db']['NAME']
        basecpf_db_path = settings.DATABASES['default']['NAME']

        # Data containers for threads
        empresa_data = [None]
        estabelecimento_data = [None]
        simples_data = [None]
        socios_data = [None]

        def fetch_cnpj_data():
            cnpj_conn = sqlite3.connect(cnpj_db_path)
            cnpj_cursor = cnpj_conn.cursor()
            try:
                empresa_data[0] = self._query_empresa(cnpj_cursor, cnpj_basico)
                estabelecimento_data[0] = self._query_estabelecimento(cnpj_cursor, cnpj_basico, cnpj_ordem, cnpj_dv)
                simples_data[0] = self._query_simples(cnpj_cursor, cnpj_basico)
                socios_data[0] = self._query_socios(cnpj_cursor, cnpj_basico)
            finally:
                cnpj_conn.close()

        def fetch_cpf_data_for_socios():
            # This function will be called after socios_data is available from fetch_cnpj_data
            # It's not truly parallel with the initial CNPJ queries, but it's separated
            pass # Actual logic will be in _enrich_socios_data

        # Run CNPJ data fetching in a separate thread
        cnpj_thread = threading.Thread(target=fetch_cnpj_data)
        cnpj_thread.start()
        cnpj_thread.join() # Wait for CNPJ data to be fetched

        if not empresa_data[0]:
            return Response({"error": "CNPJ not found."}, status=status.HTTP_404_NOT_FOUND)

        # Now enrich data and fetch CPF details for socios
        cnpj_conn_for_enrichment = sqlite3.connect(cnpj_db_path) # New connection for enrichment
        cnpj_cursor_for_enrichment = cnpj_conn_for_enrichment.cursor()

        try:
            enriched_empresa = self._enrich_empresa_data(cnpj_cursor_for_enrichment, empresa_data[0])
            enriched_estabelecimento = self._enrich_estabelecimento_data(cnpj_cursor_for_enrichment, estabelecimento_data[0])
            enriched_simples = self._enrich_simples_data(simples_data[0])

            # Fetch CPF data for socios in a separate thread
            enriched_socios_result = [None]
            def enrich_socios_thread_target():
                basecpf_conn = sqlite3.connect(basecpf_db_path)
                basecpf_cursor = basecpf_conn.cursor()
                try:
                    enriched_socios_result[0] = self._enrich_socios_data(basecpf_cursor, socios_data[0])
                finally:
                    basecpf_conn.close()

            socios_thread = threading.Thread(target=enrich_socios_thread_target)
            socios_thread.start()
            socios_thread.join()

            response_data = self._assemble_json(
                cnpj_digits,
                enriched_empresa,
                enriched_estabelecimento,
                enriched_simples,
                enriched_socios_result[0]
            )

            return Response(response_data, status=status.HTTP_200_OK)

        finally:
            cnpj_conn_for_enrichment.close()

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
        dv1_calculated = calculate_dv(cnpj_12_digits, weights1);

        # Validate first check digit
        if int(cnpj[12]) != dv1_calculated:
            return False

        # Calculate second check digit
        cnpj_13_digits = cnpj[0:13] # Includes the first calculated DV
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        dv2_calculated = calculate_dv(cnpj_13_digits, weights2);

        # Validate second check digit
        if int(cnpj[13]) != dv2_calculated:
            return False

        return True

    def _query_empresa(self, cursor, cnpj_basico):
        cursor.execute("""
            SELECT
                razao_social, natureza_juridica, qualificacao_responsavel,
                porte_empresa, ente_federativo_responsavel, capital_social
            FROM empresas
            WHERE cnpj_basico = ?;
        """, (cnpj_basico,))
        return cursor.fetchone()

    def _query_estabelecimento(self, cursor, cnpj_basico, cnpj_ordem, cnpj_dv):
        cursor.execute("""
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
        """, (cnpj_basico, cnpj_ordem, cnpj_dv))
        return cursor.fetchone()

    def _query_simples(self, cursor, cnpj_basico):
        cursor.execute("""
            SELECT
                opcao_simples, data_opcao_simples, data_exclusao_simples,
                opcao_mei, data_opcao_mei, data_exclusao_mei
            FROM simples
            WHERE cnpj_basico = ?;
        """, (cnpj_basico,))
        return cursor.fetchone()

    def _query_socios(self, cursor, cnpj_basico):
        cursor.execute("""
            SELECT
                nome_socio, cnpj_cpf_socio, qualificacao_socio,
                data_entrada_sociedade, pais, representante_legal,
                nome_representante, qualificacao_representante_legal,
                faixa_etaria
            FROM socios
            WHERE cnpj_basico = ?;
        """, (cnpj_basico,))
        return cursor.fetchall()

    def _get_description(self, cursor, table_name, code):
        if code is None:
            return None
        cursor.execute(f"""
            SELECT descricao
            FROM {table_name}
            WHERE codigo = ?;
        """, (code,))
        result = cursor.fetchone()
        return result[0] if result else None

    def _enrich_empresa_data(self, cursor, data):
        if not data:
            return {}
        
        porte_mapping = {
            '01': 'MICRO EMPRESA',
            '03': 'EMPRESA DE PEQUENO PORTE',
            '05': 'DEMAIS'
        }
        porte_descricao = porte_mapping.get(data[3], 'NAO INFORMADO')

        return {
            "razao_social": data[0],
            "natureza_juridica": {
                "codigo": data[1],
                "descricao": self._get_description(cursor, "natureza_juridica", data[1])
            },
            "qualificacao_responsavel": {
                "codigo": data[2],
                "descricao": self._get_description(cursor, "qualificacao_socio", data[2])
            },
            "porte": porte_descricao,
            "ente_federativo_responsavel": data[4],
            "capital_social": data[5]
        }

    def _enrich_estabelecimento_data(self, cursor, data):
        if not data:
            return {}
        cnae_fiscal_secundaria = []
        if data[11]: # cnae_fiscal_secundaria
            for cnae_code in data[11].split(','): # Assuming comma-separated
                cnae_fiscal_secundaria.append({
                    "codigo": cnae_code.strip(),
                    "descricao": self._get_description(cursor, "cnae", cnae_code.strip())
                })

        return {
            "cnpj_ordem": data[0],
            "cnpj_dv": data[1],
            "matriz_filial": "MATRIZ" if data[2] == '1' else "FILIAL",
            "nome_fantasia": data[3],
            "situacao_cadastral": {
                "codigo": data[4],
                "descricao": self._get_description(cursor, "motivo", data[4])
            },
            "data_situacao_cadastral": data[5],
            "motivo_situacao_cadastral": {
                "codigo": data[6],
                "descricao": self._get_description(cursor, "motivo", data[6])
            },
            "nome_cidade_exterior": data[7],
            "pais": {
                "codigo": data[8],
                "descricao": self._get_description(cursor, "pais", data[8])
            },
            "data_inicio_atividades": data[9],
            "cnae_principal": {
                "codigo": data[10],
                "descricao": self._get_description(cursor, "cnae", data[10])
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
                "descricao": self._get_description(cursor, "municipio", data[19])
            },
            "ddd1": data[20],
            "telefone1": data[21],
            "ddd2": data[22],
            "telefone2": data[23],
            "ddd_fax": data[24],
            "fax": data[25],
            "correio_eletronico": data[26],
            "situacao_especial": data[27],
            "data_situacao_especial": data[28]
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
            "data_exclusao_mei": data[5]
        }

    def _enrich_socios_data(self, basecpf_cursor, socios_data):
        enriched_socios = []
        cnpj_db_path = settings.DATABASES['cnpj_db']['NAME']
        cnpj_conn_local = sqlite3.connect(cnpj_db_path)
        cnpj_cursor_local = cnpj_conn_local.cursor()

        try:
            for socio in socios_data:
                nome_socio = socio[0]
                cpf_value = None
                sexo = None
                data_nascimento = None

                # Attempt to find CPF details by name in basecpf.db
                # WARNING: Searching by name is not a reliable method for unique identification
                # and may lead to incorrect associations if multiple individuals share the same name.
                basecpf_cursor.execute("""
                    SELECT cpf, sexo, nasc
                    FROM cpf
                    WHERE nome = ?
                    LIMIT 1;
                """, (nome_socio,))
                cpf_details = basecpf_cursor.fetchone()
                print(f"DEBUG: Searching CPF by name '{nome_socio}', Details: {cpf_details}") # Debug print
                if cpf_details:
                    cpf_value = cpf_details[0]
                    sexo = cpf_details[1]
                    data_nascimento = cpf_details[2]

                enriched_socios.append({
                    "cpf": cpf_value, # Use the unmasked CPF found by name
                    "nome": socio[0],
                    "sexo": sexo,
                    "data_nascimento": data_nascimento,
                    "qualificacao_socio": {
                        "codigo": socio[2],
                        "descricao": self._get_description(cnpj_cursor_local, "qualificacao_socio", socio[2])
                    },
                    "data_entrada_sociedade": socio[3],
                    "pais": {
                        "codigo": socio[4],
                        "descricao": self._get_description(cnpj_cursor_local, "pais", socio[4])
                    },
                    "representante_legal": socio[5],
                    "nome_representante": socio[6],
                    "qualificacao_representante_legal": {
                        "codigo": socio[7],
                        "descricao": self._get_description(cnpj_cursor_local, "qualificacao_socio", socio[7])
                    },
                    "faixa_etaria": socio[8]
                })
            return enriched_socios
        finally:
            cnpj_conn_local.close()

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
                "simples": simples,
                "endereco": {
                    "logradouro": estabelecimento.get("logradouro"),
                    "numero": estabelecimento.get("numero"),
                    "complemento": estabelecimento.get("complemento"),
                    "bairro": estabelecimento.get("bairro"),
                    "cep": estabelecimento.get("cep"),
                    "uf": estabelecimento.get("uf"),
                    "municipio": estabelecimento.get("municipio")
                },
                "atividades": {
                    "cnae_principal": estabelecimento.get("cnae_principal"),
                    "cnae_secundarias": estabelecimento.get("cnae_secundarias")
                },
                "contato": {
                    "telefone1": f"{estabelecimento.get('ddd1')} {estabelecimento.get('telefone1')}" if estabelecimento.get('ddd1') and estabelecimento.get('telefone1') else None,
                    "telefone2": f"{estabelecimento.get('ddd2')} {estabelecimento.get('telefone2')}" if estabelecimento.get('ddd2') and estabelecimento.get('telefone2') else None,
                    "fax": f"{estabelecimento.get('ddd_fax')} {estabelecimento.get('fax')}" if estabelecimento.get('ddd_fax') and estabelecimento.get('fax') else None,
                    "email": estabelecimento.get("correio_eletronico")
                },
                "situacao_cadastral": {
                    "codigo": estabelecimento.get("situacao_cadastral", {}).get("codigo"),
                    "descricao": estabelecimento.get("situacao_cadastral", {}).get("descricao"),
                    "data": estabelecimento.get("data_situacao_cadastral"),
                    "motivo": estabelecimento.get("motivo_situacao_cadastral")
                }
            },
            "socios": socios
        }
