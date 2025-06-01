import json
from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from django.urls import reverse

class ApiTests(TestCase):
    @override_settings(
        HIVEBOX_VERSION='0.1.0',
        OPENSENSEMAP_API='https://api.opensensemap.org',
        SENSEBOX_IDS=[
            "679652e79697fc0007248229",
            "631af55c8aecc5001c3298fd",
            "67837e108e3d610008017850"
        ]
    )
    def test_version_endpoint(self):
        """Test version endpoint returns correct version"""
        # Test JSON response
        response = self.client.get(
            reverse('version'),  # Removed namespace
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['version'], '0.1.0')

        # Test HTML response
        response = self.client.get(reverse('version'))  # Removed namespace
        self.assertEqual(response.status_code, 200)

    @override_settings(
        OPENSENSEMAP_API='https://api.opensensemap.org',
        SENSEBOX_IDS=[
            "679652e79697fc0007248229",
            "631af55c8aecc5001c3298fd",
            "67837e108e3d610008017850"
        ]
    )
    @patch('requests.get')
    def test_temperature_endpoint_success(self, mock_get):
        """Test successful temperature endpoint"""
        sensebox_ids = [
            "679652e79697fc0007248229",
            "631af55c8aecc5001c3298fd",
            "67837e108e3d610008017850"
        ]

        mock_responses = []
        expected_values_in_html = []
        for i, box_id in enumerate(sensebox_ids):
            mock_box_response = MagicMock()
            mock_box_response.json.return_value = {
                '_id': box_id,
                'sensors': [{
                    '_id': f'tempsensor{i+1}',
                    'title': 'temperature',
                    'unit': '°C'
                }]
            }
            mock_box_response.status_code = 200
            mock_responses.append(mock_box_response)

            mock_measurements_response = MagicMock()
            current_value = 22.5 + i * 0.5
            mock_measurements_response.json.return_value = [{
                'createdAt': f'2023-01-01T12:0{i}:00Z',
                'value': str(current_value)
            }]
            mock_measurements_response.status_code = 200
            mock_responses.append(mock_measurements_response)
            expected_values_in_html.append(str(current_value))

        mock_get.side_effect = mock_responses

        # Test JSON response
        response = self.client.get(
            reverse('temperature'),  # Removed namespace
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['samples'], len(sensebox_ids))
        
        expected_average_temp = sum(float(val) for val in expected_values_in_html) / len(expected_values_in_html)
        self.assertEqual(data['average_temp'], expected_average_temp)

        # Test HTML response
        response = self.client.get(reverse('temperature'))  # Removed namespace
        self.assertEqual(response.status_code, 200)