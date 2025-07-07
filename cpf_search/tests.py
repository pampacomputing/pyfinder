from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings

from cpf_search.views import search_cpf
from cpf_search.models import Cpf

@override_settings(ATOMIC_REQUESTS=False)
class CPFSearchFunctionTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    @patch('cpf_search.views.Cpf.objects')
    def test_search_cpf_by_cpf_valid(self, mock_cpf_objects):
        # Mock Cpf.objects.filter to return a mock QuerySet that can be iterated
        mock_cpf_queryset = MagicMock()
        mock_cpf_queryset.__iter__.return_value = [MagicMock(nome="JOHN DOE", cpf="11122233344", nasc="1980-01-01")]
        mock_cpf_objects.filter.return_value = mock_cpf_queryset

        # Mock related company and socios data if necessary for full flow
        mock_socios_objects.using.return_value.filter.return_value.values.return_value.distinct.return_value = MagicMock(__iter__=MagicMock(return_value=[]))

        response = self.client.post('/api/search/', {"cpf": "111.222.333-44"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user_data", response.data)
        self.assertEqual(len(response.data["user_data"]), 1)
        self.assertEqual(response.data["user_data"][0]["cpf"], "11122233344")
        self.assertEqual(response.data["user_data"][0]["name"], "JOHN DOE")

    @patch('cpf_search.views.Cpf.objects')
    def test_search_cpf_by_cpf_not_found(self, mock_cpf_objects):
        # Mock Cpf.objects.filter to return an empty queryset
        mock_cpf_queryset = MagicMock()
        mock_cpf_queryset.__iter__.return_value = []
        mock_cpf_objects.filter.return_value = mock_cpf_queryset

        response = self.client.post('/api/search/', {"cpf": "999.999.999-99"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user_data", response.data)
        self.assertEqual(len(response.data["user_data"]), 0)

    @patch('cpf_search.views.Cpf.objects')
    @patch('cpf_search.views.Empresas.objects')
    @patch('cpf_search.views.Socios.objects')
    def test_search_cpf_by_name_valid(self, mock_socios_objects, mock_empresas_objects, mock_cpf_objects):
        # Mock Cpf.objects.filter to return a valid CPF
        mock_cpf_queryset = MagicMock()
        mock_cpf_queryset.__iter__.return_value = [MagicMock(nome="JANE DOE", cpf="55566677788", nasc="1990-05-10")]
        mock_cpf_objects.filter.return_value = mock_cpf_queryset

        # Mock related company and socios data if necessary for full flow
        mock_socios_objects.using.return_value.filter.return_value.values.return_value.distinct.return_value = MagicMock(__iter__=MagicMock(return_value=[]))

        response = self.client.post('/api/search/', {"name": "JANE DOE"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user_data", response.data)
        self.assertEqual(len(response.data["user_data"]), 1)
        self.assertEqual(response.data["user_data"][0]["name"], "JANE DOE")

    

    @patch('cpf_search.views.Empresas.objects')
    @patch('cpf_search.views.Socios.objects')
    def test_search_cpf_by_cnpj_not_found(self, mock_socios_objects, mock_empresas_objects):
        # Mock Empresas.objects.using to return an empty list
        mock_empresas_queryset = MagicMock()
        mock_empresas_queryset.values.return_value = []
        mock_empresas_objects.using.return_value.filter.return_value = mock_empresas_queryset

        mock_socios_queryset = MagicMock()
        mock_socios_queryset.values.return_value = []
        mock_socios_objects.using.return_value.filter.return_value = mock_socios_queryset

        response = self.client.post('/api/search/', {"cnpj": "99.999.999/0001-99"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("company_data", response.data)
        self.assertFalse(response.data["company_data"])
        self.assertIn("partners_data", response.data)
        self.assertEqual(len(response.data["partners_data"]), 0)

    def test_search_cpf_no_params(self):
        response = self.client.post('/api/search/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user_data", response.data)
        self.assertEqual(len(response.data["user_data"]), 0)
        self.assertIn("company_data", response.data)
        self.assertFalse(response.data["company_data"])
        self.assertIn("partners_data", response.data)
        self.assertEqual(len(response.data["partners_data"]), 0)