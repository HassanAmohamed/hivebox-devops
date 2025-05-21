from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': os.getenv('MONGO_DB_NAME', 'testdb'),
        'CLIENT': {
            'host': os.getenv('MONGO_HOST', 'mongodb://root:example@localhost:27017'),
            'username': 'root',
            'password': 'example',
            'authSource': 'admin',
            'authMechanism': 'SCRAM-SHA-1'
        },
        'TEST': {
            'NAME': 'testdb',
        }
    }
}

# Disable migrations for tests
MIGRATION_MODULES = {
    'app_name': None,  # replace 'app_name' with your actual app names
}

# Speed up tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]