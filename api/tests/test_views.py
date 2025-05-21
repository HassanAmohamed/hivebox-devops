from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from django.urls import reverse
import json
from datetime import datetime, timedelta
import time

class ApiTests(TestCase):
    @override_settings(HIVEBOX_VERSION='0.1.0')
    def test_version_endpoint(self):
        """Test version endpoint returns correct version"""
        response = self.client.get(reverse('version'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['version'], '0.1.0')

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
            response = self.client.get(reverse('temperature'))
            
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['samples'], 1)

    @patch('requests.get')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_temperature_endpoint_retry(self, mock_sleep, mock_get):
        """Test retry logic for rate limiting"""
        test_box_id = "testbox123"
        
        # First mock response (box info)
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
        
        # First measurements response (409 error)
        mock_409_response = MagicMock()
        mock_409_response.status_code = 409
        mock_409_response.headers = {'Retry-After': '1'}
        
        # Second measurements response (success)
        mock_success_response = MagicMock()
        mock_success_response.json.return_value = [{
            'createdAt': '2023-01-01T12:00:00Z',
            'value': '22.5'
        }]
        mock_success_response.status_code = 200
        
        mock_get.side_effect = [
            mock_box_response,
            mock_409_response,
            mock_success_response
        ]
        
        with override_settings(SENSEBOX_IDS=[test_box_id]):
            response = self.client.get(reverse('temperature'))
            
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['samples'], 1)
        mock_sleep.assert_called_once_with(1)  # Verify sleep was called with Retry-After value

    @patch('requests.get')
    @patch('time.sleep')
    def test_temperature_endpoint_rate_limit_exceeded(self, mock_sleep, mock_get):
        """Test handling when rate limit is exceeded"""
        test_box_id = "testbox123"
        
        # Mock responses
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
        
        mock_409_response = MagicMock()
        mock_409_response.status_code = 409
        mock_409_response.headers = {}
        
        mock_get.side_effect = [
            mock_box_response,
            mock_409_response,
            mock_409_response,
            mock_409_response
        ]
        
        with override_settings(SENSEBOX_IDS=[test_box_id], MAX_RETRIES=3):
            response = self.client.get(reverse('temperature'))
            
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(mock_sleep.call_count, 2)  # Should retry MAX_RETRIES-1 times