from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.conf import settings
import requests, logging, time
from django.core.cache import cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

# Cache timeout in seconds (5 minutes)
CACHE_TIMEOUT = 300
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

def _should_return_json(request):
    """Helper function to determine response format"""
    return (
        request.headers.get('Accept') == 'application/json' or
        request.GET.get('format') == 'json'
    )

@require_GET
def home(request):
    """Render the home page for the HiveBox app."""
    if _should_return_json(request):
        return JsonResponse({'message': 'HiveBox API'})
    return render(request, 'api/home.html')

@require_GET
def version(request):
    """Return current app version."""
    data = {'version': settings.HIVEBOX_VERSION}
    if _should_return_json(request):
        return JsonResponse(data)
    return render(request, 'api/version.html', data)

@require_GET
def temperature(request):
    """Return average temperature from SenseBoxes with improved error handling."""
    cache_key = f"temperature_data_{'_'.join(settings.SENSEBOX_IDS)}"
    cached_data = cache.get(cache_key)

    if cached_data:
        logger.debug("Returning cached temperature data")
        if _should_return_json(request):
            return JsonResponse(cached_data)
        return render(request, 'api/temperature.html', cached_data)

    temperatures = []
    errors = []
    successful_boxes = 0

    for box_id in settings.SENSEBOX_IDS:
        for attempt in range(MAX_RETRIES):
            try:
                # First check if box exists
                box_url = f"{settings.OPENSENSEMAP_API}/boxes/{box_id}"
                box_response = requests.get(box_url, timeout=5)

                if box_response.status_code == 404:
                    error_msg = f"SenseBox {box_id} not found or no longer available"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    break

                box_response.raise_for_status()
                box_data = box_response.json()
                logger.debug(f"Box data for {box_id}: {box_data}")

                # Find temperature sensor - expanded to match more title variations
                valid_titles = ['temperature', 'Temperature', 'Temperatur', 'temp', 'Temp', 'Lufttemperatur']
                temp_sensor = next(
                    (s for s in box_data.get('sensors', [])
                    if any(title.lower() in s.get('title', '').lower() for title in valid_titles)),
                    None
                )

                if not temp_sensor:
                    error_msg = f"No temperature sensor found for box {box_id}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    break

                # Get measurements from last hour with proper date formatting
                measurements_url = f"{settings.OPENSENSEMAP_API}/boxes/{box_id}/data/{temp_sensor['_id']}"
                from_date = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
                params = {
                    'from-date': from_date,
                    'format': 'json'
                }

                measurements_response = requests.get(measurements_url, params=params, timeout=5)

                if measurements_response.status_code == 409:
                    # Handle rate limiting - wait and retry
                    if attempt < MAX_RETRIES - 1:
                        retry_after = measurements_response.headers.get('Retry-After', RETRY_DELAY)
                        logger.warning(f"Rate limited. Waiting {retry_after} seconds before retry {attempt + 1}")
                        time.sleep(float(retry_after))
                        continue
                    else:
                        error_msg = f"Rate limit exceeded for box {box_id} after {MAX_RETRIES} attempts"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        break

                measurements_response.raise_for_status()
                measurements = measurements_response.json()

                if not measurements:
                    error_msg = f"No recent measurements for box {box_id}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    break

                # Get most recent measurement
                latest = max(measurements, key=lambda x: x['createdAt'])
                temperatures.append(float(latest['value']))
                successful_boxes += 1
                logger.info(f"Successfully retrieved data for box {box_id}")
                break  # Success - exit retry loop

            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    error_msg = f"Network error for box {box_id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                time.sleep(RETRY_DELAY)
            except (ValueError, KeyError) as e:
                error_msg = f"Data processing error for box {box_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                break
            except Exception as e:
                error_msg = f"Unexpected error for box {box_id}: {str(e)}"
                logger.exception(error_msg)
                errors.append(error_msg)
                break

    response_data = {
        "average_temp": round(sum(temperatures) / len(temperatures), 2) if temperatures else None,
        "unit": "°C",
        "samples": len(temperatures),
        "successful_boxes": successful_boxes,
        "total_boxes": len(settings.SENSEBOX_IDS),
        "timestamp": datetime.now().isoformat(),
        "errors": errors,
    }

    if not temperatures:
        response_data['error'] = "Could not retrieve temperature data from any SenseBox"
        logger.error("Failed to retrieve temperature data from all SenseBoxes")
    else:
        cache.set(cache_key, response_data, CACHE_TIMEOUT)

    if _should_return_json(request):
        return JsonResponse(response_data)
    return render(request, 'api/temperature.html', response_data)