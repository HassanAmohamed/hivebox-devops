import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRET_KEY = 'dummy-key-for-testing'
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'api',  # your app
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ROOT_URLCONF = 'api.urls'
TIME_ZONE = 'UTC'
USE_TZ = True

# Custom settings for your app
HIVEBOX_VERSION = '0.1.0'
SENSEBOX_IDS = []
MAX_RETRIES = 3