import pytest
from django.test import RequestFactory

@pytest.fixture
def factory():
    return RequestFactory()

# Add any other fixtures your tests might need