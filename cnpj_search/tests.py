from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings
import sqlite3
import os

from cnpj_search.views import CNPJSearchView

@override_settings(ATOMIC_REQUESTS=False)
class CNPJSearchViewUnitTests(TestCase):

    def setUp(self):
        # Reset mocks before each test to ensure isolation
        if hasattr(self, 'mock_cursor'):
            self.mock_cursor.reset_mock()

    def test_validate_cnpj_check_digits_valid(self):
        # Valid CNPJ from a real example (e.g., Petrobras)
        valid_cnpj = "33000167000101"
        self.assertTrue(CNPJSearchView()._validate_cnpj_check_digits(valid_cnpj))

        # Another valid CNPJ
        valid_cnpj_2 = "00000000000191"
        self.assertTrue(CNPJSearchView()._validate_cnpj_check_digits(valid_cnpj_2))

    def test_validate_cnpj_check_digits_invalid(self):
        # Invalid first digit
        invalid_cnpj_dv1 = "33000167000102" # Should be 01
        self.assertFalse(CNPJSearchView()._validate_cnpj_check_digits(invalid_cnpj_dv1))

        # Invalid second digit
        invalid_cnpj_dv2 = "33000167000110" # Should be 01
        self.assertFalse(CNPJSearchView()._validate_cnpj_check_digits(invalid_cnpj_dv2))

        # Completely invalid
        invalid_cnpj_random = "12345678901234"
        self.assertFalse(CNPJSearchView()._validate_cnpj_check_digits(invalid_cnpj_random))

    @patch('sqlite3.connect')
    def test_query_empresa(self, mock_sqlite_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (
            "TEST COMPANY LTDA", "2062", "10", "01", "BRAZIL", 100000.00
        )

        result = CNPJSearchView()._query_empresa(mock_cursor, "12345678")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "TEST COMPANY LTDA")
        mock_cursor.execute.assert_called_once()

    @patch('sqlite3.connect')
    def test_query_estabelecimento(self, mock_sqlite_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (
            "0001", "95", "1", "TEST FANTASY NAME", "02", "20200101", "00", None, "1058", "20100101",
            "6201503", "6202300,6311900", "RUA", "TEST STREET", "123", "APT 1", "CENTRO", "12345000",
            "SP", "3550308", "11", "12345678", None, None, None, None, "test@example.com", None, None
        )

        result = CNPJSearchView()._query_estabelecimento(mock_cursor, "12345678", "0001", "95")
        self.assertIsNotNone(result)
        self.assertEqual(result[3], "TEST FANTASY NAME")
        mock_cursor.execute.assert_called_once()

    @patch('sqlite3.connect')
    def test_query_simples(self, mock_sqlite_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (
            1, "20180101", None, 0, None, None
        )

        result = CNPJSearchView()._query_simples(mock_cursor, "12345678")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 1)
        mock_cursor.execute.assert_called_once()

    @patch('sqlite3.connect')
    def test_query_socios(self, mock_sqlite_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ("PARTNER ONE", "***12345678", "10", "20150101", "1058", None, None, None, "30-40"),
            ("PARTNER TWO", "***87654321", "20", "20160601", "1058", None, None, None, "40-50"),
        ]

        result = CNPJSearchView()._query_socios(mock_cursor, "12345678")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "PARTNER ONE")
        mock_cursor.execute.assert_called_once()

    @patch('sqlite3.connect')
    def test_enrich_empresa_data(self, mock_sqlite_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock _get_description calls
        mock_cursor.fetchone.side_effect = [
            ("Sociedade Empresária Limitada",), # natureza_juridica
            ("Administrador",), # qualificacao_socio
        ]

        empresa_raw_data = ("TEST COMPANY LTDA", "2062", "10", "01", "BRAZIL", 100000.00)
        enriched_data = CNPJSearchView()._enrich_empresa_data(mock_cursor, empresa_raw_data)

        self.assertEqual(enriched_data["razao_social"], "TEST COMPANY LTDA")
        self.assertEqual(enriched_data["natureza_juridica"]["descricao"], "Sociedade Empresária Limitada")
        self.assertEqual(enriched_data["porte"], "MICRO EMPRESA")

    @patch('sqlite3.connect')
    def test_enrich_estabelecimento_data(self, mock_sqlite_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock _get_description calls
        mock_cursor.fetchone.side_effect = [
            ("ATIVA",), # situacao_cadastral
            ("SEM MOTIVO",), # motivo_situacao_cadastral
            ("BRASIL",), # pais
            ("Desenvolvimento de programas de computador sob encomenda",), # cnae_principal
            ("Consultoria em tecnologia da informação",), # cnae_secundaria 1
            ("Tratamento de dados, provedores de serviços de aplicação e serviços de hospedagem na internet",), # cnae_secundaria 2
            ("SÃO PAULO",), # municipio
        ]

        estabelecimento_raw_data = (
            "0001", "95", "1", "TEST FANTASY NAME", "02", "20200101", "00", None, "1058", "20100101",
            "6201503", "6202300,6311900", "RUA", "TEST STREET", "123", "APT 1", "CENTRO", "12345000",
            "SP", "3550308", "11", "98765432", "11", "12345678", None, None, "test@example.com", None, None
        )
        enriched_data = CNPJSearchView()._enrich_estabelecimento_data(mock_cursor, estabelecimento_raw_data)

        self.assertEqual(enriched_data["nome_fantasia"], "TEST FANTASY NAME")
        self.assertEqual(enriched_data["situacao_cadastral"]["descricao"], "ATIVA")
        self.assertEqual(enriched_data["cnae_principal"]["descricao"], "DESENVOLVIMENTO DE SOFTWARE")
        self.assertEqual(len(enriched_data["cnae_secundarias"]), 2)

    def test_enrich_simples_data(self):
        simples_raw_data = (1, "20180101", None, 0, None, None)
        enriched_data = CNPJSearchView()._enrich_simples_data(simples_raw_data)

        self.assertTrue(enriched_data["opcao_simples"])
        self.assertEqual(enriched_data["data_opcao_simples"], "20180101")
        self.assertFalse(enriched_data["opcao_mei"])

    @patch('sqlite3.connect')
    def test_enrich_socios_data(self, mock_sqlite_connect):
        mock_cnpj_conn = MagicMock()
        mock_cnpj_cursor = MagicMock()
        mock_basecpf_conn = MagicMock()
        mock_basecpf_cursor = MagicMock()

        mock_sqlite_connect.side_effect = [mock_cnpj_conn, mock_basecpf_conn] # First call for cnpj, second for basecpf
        mock_cnpj_conn.cursor.return_value = mock_cnpj_cursor
        mock_basecpf_conn.cursor.return_value = mock_basecpf_cursor

        # Mock _get_description calls for cnpj_cursor
        mock_cnpj_cursor.fetchone.side_effect = [
            ("Sócio Administrador",), # qualificacao_socio
            ("BRASIL",), # pais
            ("Procurador",), # qualificacao_representante_legal
        ]

        # Mock basecpf_cursor.execute for CPF lookup by name
        mock_basecpf_cursor.fetchone.return_value = ("12345678901", "M", "1980-01-01")

        socios_raw_data = [
            ("PARTNER ONE", "***12345678", "10", "20150101", "1058", None, None, None, "30-40"),
        ]

        enriched_data = CNPJSearchView()._enrich_socios_data(mock_basecpf_cursor, socios_raw_data)

        self.assertEqual(enriched_data[0]["cpf"], "12345678901")
        self.assertEqual(enriched_data[0]["sexo"], "M")
        self.assertEqual(enriched_data[0]["data_nascimento"], "1980-01-01")
        self.assertEqual(enriched_data[0]["qualificacao_socio"]["descricao"], "Sócio Administrador")

    @patch('sqlite3.connect')
    def test_post_valid_cnpj(self, mock_sqlite_connect):
        client = APIClient()

        mock_cnpj_conn = MagicMock()
        mock_cnpj_cursor = MagicMock()
        mock_basecpf_conn = MagicMock()
        mock_basecpf_cursor = MagicMock()

        mock_sqlite_connect.side_effect = [mock_cnpj_conn, mock_basecpf_conn, mock_cnpj_conn, mock_basecpf_conn] # Connections for main thread and then for _enrich_socios_data
        mock_cnpj_conn.cursor.return_value = mock_cnpj_cursor
        mock_basecpf_conn.cursor.return_value = mock_basecpf_cursor

        # Mock _query_empresa
        mock_cnpj_cursor.fetchone.side_effect = [
            ("TEST COMPANY LTDA", "2062", "10", "01", "BRAZIL", 100000.00), # empresa
            ("0001", "95", "1", "TEST FANTASY NAME", "02", "20200101", "00", None, "1058", "20100101",
             "6201503", "6202300,6311900", "RUA", "TEST STREET", "123", "APT 1", "CENTRO", "12345000",
             "SP", "3550308", "11", "12345678", None, None, None, None, "test@example.com", None, None), # estabelecimento
            (1, "20180101", None, 0, None, None), # simples
            ("Sócio Administrador",), # _get_description for qualificacao_socio
            ("BRASIL",), # _get_description for pais
            ("Procurador",), # _get_description for qualificacao_representante_legal
            ("Sociedade Empresária Limitada",), # _get_description for natureza_juridica
            ("Administrador",), # _get_description for qualificacao_responsavel
            ("ATIVA",), # _get_description for situacao_cadastral
            ("SEM MOTIVO",), # _get_description for motivo_situacao_cadastral
            ("BRASIL",), # _get_description for pais
            ("Desenvolvimento de programas de computador sob encomenda",), # cnae_principal
            ("Consultoria em tecnologia da informação",), # cnae_secundaria 1
            ("Tratamento de dados, provedores de serviços de aplicação e serviços de hospedagem na internet",), # cnae_secundaria 2
            ("SÃO PAULO",), # municipio
        ]

        # Mock _query_socios
        mock_cnpj_cursor.fetchall.return_value = [
            ("PARTNER ONE", "***12345678", "10", "20150101", "1058", None, None, None, "30-40"),
        ]

        # Mock basecpf_cursor.fetchone for CPF lookup by name
        mock_basecpf_cursor.fetchone.return_value = ("12345678901", "M", "1980-01-01")

        response = client.post('/api/cnpj/search/', {"cnpj": "33000167000101"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("cnpj", response.data)
        self.assertIn("empresa", response.data)
        self.assertIn("socios", response.data)
        self.assertEqual(response.data["empresa"]["razao_social"], "TEST COMPANY LTDA")
        self.assertEqual(response.data["socios"][0]["cpf"], "12345678901")

    def test_post_invalid_cnpj(self):
        client = APIClient()
        response = client.post('/api/cnpj/search/', {"cnpj": "123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_post_cnpj_not_found(self):
        client = APIClient()
        with patch('sqlite3.connect') as mock_sqlite_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_sqlite_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None # Simulate no company found

            response = client.post('/api/cnpj/search/', {"cnpj": "99999999999999"}, format='json')
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn("error", response.data)


@override_settings(ATOMIC_REQUESTS=False)
class CNPJIntegrationTests(TestCase):
    # Store original database settings
    _original_cnpj_db_name = None
    _original_default_db_name = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Save original database settings
        cls._original_cnpj_db_name = settings.DATABASES['cnpj_db']['NAME']
        cls._original_default_db_name = settings.DATABASES['default']['NAME']

        # Set up in-memory databases for testing
        settings.DATABASES['cnpj_db'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }

        # Connect to in-memory databases and populate them
        cls.cnpj_conn = sqlite3.connect(settings.DATABASES['cnpj_db']['NAME'])
        cls.basecpf_conn = sqlite3.connect(settings.DATABASES['default']['NAME'])
        cls._create_and_populate_cnpj_db(cls.cnpj_conn)
        cls._create_and_populate_basecpf_db(cls.basecpf_conn)

        # Add ATOMIC_REQUESTS to settings for testing
        if not hasattr(settings, 'ATOMIC_REQUESTS'):
            settings.ATOMIC_REQUESTS = False

    @classmethod
    def tearDownClass(cls):
        # Close connections
        cls.cnpj_conn.close()
        cls.basecpf_conn.close()

        # Restore original database settings
        settings.DATABASES['cnpj_db']['NAME'] = cls._original_cnpj_db_name
        settings.DATABASES['default']['NAME'] = cls._original_default_db_name
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()

    @staticmethod
    def _create_and_populate_cnpj_db(conn):
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE empresas (
                cnpj_basico TEXT PRIMARY KEY,
                razao_social TEXT,
                natureza_juridica TEXT,
                qualificacao_responsavel TEXT,
                porte_empresa TEXT,
                ente_federativo_responsavel TEXT,
                capital_social REAL
            );
        """)
        cursor.execute("""
            CREATE TABLE estabelecimento (
                cnpj_basico TEXT,
                cnpj_ordem TEXT,
                cnpj_dv TEXT,
                matriz_filial TEXT,
                nome_fantasia TEXT,
                situacao_cadastral TEXT,
                data_situacao_cadastral TEXT,
                motivo_situacao_cadastral TEXT,
                nome_cidade_exterior TEXT,
                pais TEXT,
                data_inicio_atividades TEXT,
                cnae_fiscal TEXT,
                cnae_fiscal_secundaria TEXT,
                tipo_logradouro TEXT,
                logradouro TEXT,
                numero TEXT,
                complemento TEXT,
                bairro TEXT,
                cep TEXT,
                uf TEXT,
                municipio TEXT,
                ddd1 TEXT,
                telefone1 TEXT,
                ddd2 TEXT,
                telefone2 TEXT,
                ddd_fax TEXT,
                fax TEXT,
                correio_eletronico TEXT,
                situacao_especial TEXT,
                data_situacao_especial TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE simples (
                cnpj_basico TEXT PRIMARY KEY,
                opcao_simples INTEGER,
                data_opcao_simples TEXT,
                data_exclusao_simples TEXT,
                opcao_mei INTEGER,
                data_opcao_mei TEXT,
                data_exclusao_mei TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE socios (
                cnpj_basico TEXT,
                nome_socio TEXT,
                cnpj_cpf_socio TEXT,
                qualificacao_socio TEXT,
                data_entrada_sociedade TEXT,
                pais TEXT,
                representante_legal TEXT,
                nome_representante TEXT,
                qualificacao_representante_legal TEXT,
                faixa_etaria TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE natureza_juridica (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE qualificacao_socio (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            );
        """
        )
        cursor.execute("""
            CREATE TABLE motivo (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            );
        """
        )
        cursor.execute("""
            CREATE TABLE pais (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            );
        """
        )
        cursor.execute("""
            CREATE TABLE cnae (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            );
        """
        )
        cursor.execute("""
            CREATE TABLE municipio (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            );
        """
        )

        # Insert sample data
        cursor.execute("INSERT INTO empresas VALUES (?,?,?,?,?,?,?)",
                       ("12345678", "TEST COMPANY S.A.", "2062", "10", "01", "BRAZIL", 500000.00))
        cursor.execute("INSERT INTO estabelecimento VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       ("12345678", "0001", "95", "1", "TEST BRANCH", "02", "20230101", "00", None, "1058", "20150501",
                        "6201501", "6202300,6311900", "AVENIDA", "PRINCIPAL", "1000", "SALA 1", "CENTRO", "12345-000",
                        "SP", "3550308", "11", "98765432", "11", "12345678", None, None, "contact@test.com", None, None))
        cursor.execute("INSERT INTO simples VALUES (?,?,?,?,?,?,?)",
                       ("12345678", 1, "20180101", None, 0, None, None))
        cursor.execute("INSERT INTO socios VALUES (?,?,?,?,?,?,?,?,?,?)",
                       ("12345678", "JOHN DOE", "***11122233", "10", "20150501", "1058", None, None, None, "30-40"))
        cursor.execute("INSERT INTO natureza_juridica VALUES (?,?)", ("2062", "Sociedade Empresária Limitada"))
        cursor.execute("INSERT INTO qualificacao_socio VALUES (?,?)", ("10", "Sócio Administrador"))
        cursor.execute("INSERT INTO motivo VALUES (?,?)", ("02", "ATIVA"))
        cursor.execute("INSERT INTO motivo VALUES (?,?)", ("00", "SEM MOTIVO"))
        cursor.execute("INSERT INTO pais VALUES (?,?)", ("1058", "BRASIL"))
        cursor.execute("INSERT INTO cnae VALUES (?,?)", ("6201501", "Desenvolvimento de programas de computador sob encomenda"))
        cursor.execute("INSERT INTO cnae VALUES (?,?)", ("6202300", "Consultoria em tecnologia da informação"))
        cursor.execute("INSERT INTO cnae VALUES (?,?)", ("6311900", "Tratamento de dados, provedores de serviços de aplicação e serviços de hospedagem na internet"))
        cursor.execute("INSERT INTO municipio VALUES (?,?)", ("3550308", "SÃO PAULO"))

        conn.commit()

    @staticmethod
    def _create_and_populate_basecpf_db(conn):
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE cpf (
                cpf TEXT PRIMARY KEY,
                nome TEXT,
                sexo TEXT,
                nasc TEXT
            );
        """)
        cursor.execute("INSERT INTO cpf VALUES (?,?,?,?)", ("11122233344", "JOHN DOE", "M", "1980-01-01"))

        conn.commit()

    def test_integration_cnpj_search(self):
        # Use a known valid CNPJ from the test data
        test_cnpj = "12345678000195"
        response = self.client.post('/api/cnpj/search/', {"cnpj": test_cnpj}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("cnpj", response.data)
        self.assertIn("empresa", response.data)
        self.assertIn("socios", response.data)

        # Assert company data
        self.assertEqual(response.data["cnpj"], test_cnpj)
        self.assertEqual(response.data["empresa"]["razao_social"], "TEST COMPANY S.A.")
        self.assertEqual(response.data["empresa"]["natureza_juridica"]["descricao"], "Sociedade Empresária Limitada")
        self.assertEqual(response.data["empresa"]["porte"], "MICRO EMPRESA")
        self.assertEqual(response.data["empresa"]["capital_social"], 500000.00)

        # Assert establishment data (some key fields)
        self.assertEqual(response.data["empresa"]["nome_fantasia"], "TEST BRANCH")
        self.assertEqual(response.data["empresa"]["endereco"]["cep"], "12345-000")
        self.assertEqual(response.data["empresa"]["contato"]["email"], "contact@test.com")
        self.assertEqual(response.data["empresa"]["situacao_cadastral"]["descricao"], "ATIVA")

        # Assert socios data
        self.assertEqual(len(response.data["socios"]), 1)
        self.assertEqual(response.data["socios"][0]["nome"], "JOHN DOE")
        self.assertEqual(response.data["socios"][0]["cpf"], "11122233344")
        self.assertEqual(response.data["socios"][0]["sexo"], "M")
        self.assertEqual(response.data["socios"][0]["data_nascimento"], "1980-01-01")
        self.assertEqual(response.data["socios"][0]["qualificacao_socio"]["descricao"], "Sócio Administrador")
