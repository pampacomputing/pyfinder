from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class SimpleURLTest(TestCase):
    def test_cpf_search_url_resolves(self):
        client = APIClient()
        response = client.post('/api/search/', {"cpf": "11122233344"}, format='json')
        # We expect a 200 OK if the URL resolves and the view is hit, even if the data is invalid
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
