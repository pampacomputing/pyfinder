from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings
import sqlite3
import os

from cpf_search.views import CPFSearchView

@override_settings(ATOMIC_REQUESTS=False)
class CPFSearchViewUnitTests(TestCase):

    def setUp(self):
        # Reset mocks before each test to ensure isolation
        if hasattr(self, 'mock_cursor'):
            self.mock_cursor.reset_mock()

    def test_validate_cpf_check_digits_valid(self):
        # Valid CPF examples
        self.assertTrue(CPFSearchView()._validate_cpf_check_digits("11122233344"))
        self.assertTrue(CPFSearchView()._validate_cpf_check_digits("00000000000"))

    def test_validate_cpf_check_digits_invalid(self):
        # Invalid CPF examples
        self.assertFalse(CPFSearchView()._validate_cpf_check_digits("11122233345")) # Invalid last digit
        self.assertFalse(CPFSearchView()._validate_cpf_check_digits("12345678901")) # Completely invalid
        self.assertFalse(CPFSearchView()._validate_cpf_check_digits("11111111111")) # All same digits

    @patch('sqlite3.connect')
    def test_query_cpf(self, mock_sqlite_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = ("JOHN DOE", "M", "1980-01-01")

        result = CPFSearchView()._query_cpf(mock_cursor, "11122233344")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "JOHN DOE")
        mock_cursor.execute.assert_called_once()

    @patch('sqlite3.connect')
    def test_post_valid_cpf(self, mock_sqlite_connect):
        client = APIClient()

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = ("JOHN DOE", "M", "1980-01-01")

        response = client.post('/api/cpf/search/', {"cpf": "11122233344"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("cpf", response.data)
        self.assertIn("nome", response.data)
        self.assertEqual(response.data["nome"], "JOHN DOE")

    def test_post_invalid_cpf(self):
        client = APIClient()
        response = client.post('/api/cpf/search/', {"cpf": "123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_post_cpf_not_found(self):
        client = APIClient()
        with patch('sqlite3.connect') as mock_sqlite_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_sqlite_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None # Simulate no CPF found

            response = client.post('/api/cpf/search/', {"cpf": "99999999999"}, format='json')
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn("error", response.data)


@override_settings(ATOMIC_REQUESTS=False)
class CPFIntegrationTests(TestCase):
    _original_default_db_name = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._original_default_db_name = settings.DATABASES['default']['NAME']

        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }

        cls.basecpf_conn = sqlite3.connect(settings.DATABASES['default']['NAME'])
        cls._create_and_populate_basecpf_db(cls.basecpf_conn)

        if not hasattr(settings, 'ATOMIC_REQUESTS'):
            settings.ATOMIC_REQUESTS = False

    @classmethod
    def tearDownClass(cls):
        cls.basecpf_conn.close()
        settings.DATABASES['default']['NAME'] = cls._original_default_db_name
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()

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

    def test_integration_cpf_search(self):
        test_cpf = "11122233344"
        response = self.client.post('/api/cpf/search/', {"cpf": test_cpf}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("cpf", response.data)
        self.assertIn("nome", response.data)
        self.assertEqual(response.data["cpf"], test_cpf)
        self.assertEqual(response.data["nome"], "JOHN DOE")
        self.assertEqual(response.data["sexo"], "M")
        self.assertEqual(response.data["data_nascimento"], "1980-01-01")
