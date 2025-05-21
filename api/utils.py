from django.conf import settings
from datetime import datetime, timedelta
import requests


def fetch_sensbox_data(box_id, sensor_type = 'temperature', max_age_hourse = 1):
    ''' Help func to fetch sensor data '''
    try:
        ''' get sensor id from request type '''
        response = requests.get(
            f"{settings.OPENSENSEMAP_API}/boxes/{box_id}/sensors", timeout = 5 )
        
        response.raise_for_status()
        sensors = response.json()

        sensor = next(sens for sens in sensors if sens.get('title', '').lower() == sensor_type.lower()),
        None 

        if not sensor:
            return None
        
        ''' get measurements from last max_age_hours'''
        response = requests.get(f"{settings.OPENSENSEMAP_API}/boxes/{box_id}/data/{sensor['_id']}",
        params={'from-date': (datetime.now() - timedelta(hours=max_age_hourse)).isoformat()},
        timeout = 5)
        response.raise_for_status()

        return response.json if response.json() else None
    
    except (requests.RequestException, ValueError, KeyError) as e:
        raise ValueError(f"Error fetching data for box {box_id}: {str(e)}")
        

            
        