from .base import *

# Test-specific settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Required settings for tests
OPENSENSEMAP_API = 'https://api.opensensemap.org'
SENSEBOX_IDS = [
    "679652e79697fc0007248229",  
    "631af55c8aecc5001c3298fd",  
    "67837e108e3d610008017850"   
]
HIVEBOX_VERSION = '0.1.0'  # Default version for tests