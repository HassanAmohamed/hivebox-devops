from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from django.urls import reverse
import json

class ApiTests(TestCase):
    @override_settings(HIVEBOX_VERSION='0.1.0')
    def test_version_endpoint(self):
        """Test version endpoint returns correct version"""
        response = self.client.get(reverse('version'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['version'], '0.1.0')

    # ... rest of your existing test code ...