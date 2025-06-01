from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from django.urls import reverse
import json

class ApiTests(TestCase):
    @override_settings(HIVEBOX_VERSION='0.1.0')
    def test_version_endpoint(self):
        """Test version endpoint returns correct version"""
        # Test JSON response
        response = self.client.get(
            reverse('version'),
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['version'], '0.1.0')
        
        # Test HTML response
        response = self.client.get(reverse('version'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, settings.HIVEBOX_VERSION)

    @patch('requests.get')
    def test_temperature_endpoint_success(self, mock_get):
        """Test successful temperature endpoint"""
        test_box_id = "testbox123"
        
        # Setup mock responses
        mock_box_response = MagicMock()
        mock_box_response.json.return_value = {
            '_id': test_box_id,
            'sensors': [{
                '_id': 'tempsensor123',
                'title': 'temperature',
                'unit': '°C'
            }]
        }
        mock_box_response.status_code = 200
        
        mock_measurements_response = MagicMock()
        mock_measurements_response.json.return_value = [{
            'createdAt': '2023-01-01T12:00:00Z',
            'value': '22.5'
        }]
        mock_measurements_response.status_code = 200
        
        mock_get.side_effect = [
            mock_box_response,
            mock_measurements_response
        ]
        
        with override_settings(SENSEBOX_IDS=[test_box_id]):
            # Test JSON response
            response = self.client.get(
                reverse('temperature'),
                HTTP_ACCEPT='application/json'
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(data['samples'], 1)
            
            # Test HTML response
            response = self.client.get(reverse('temperature'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "22.5")

    # ... rest of your existing test cases ...