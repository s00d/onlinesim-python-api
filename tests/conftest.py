"""
Pytest configuration and common fixtures for onlinesim-python-api tests

This file contains:
- Pytest configuration
- Common test fixtures
- Shared test utilities
"""

import pytest
import sys
import os
from unittest.mock import Mock

# Add the project root to Python path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory path"""
    return os.path.join(os.path.dirname(__file__), '..')


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory path"""
    return os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture
def mock_driver():
    """Create a mock Driver instance for testing"""
    mock = Mock()
    mock.api_key = "test_api_key_123"
    return mock


@pytest.fixture
def mock_user_service():
    """Create a mock user service for testing"""
    mock = Mock()
    mock.balance.return_value = {
        "balance": 100.00,
        "zbalance": 25.00,
        "income": 75.00
    }
    mock.profile.return_value = {
        "username": "testuser",
        "email": "test@example.com",
        "status": "active"
    }
    return mock


@pytest.fixture
def mock_numbers_service():
    """Create a mock numbers service for testing"""
    mock = Mock()
    mock.get_numbers.return_value = [
        {
            "number": "+79001234567",
            "country": 7,
            "service": "telegram",
            "price": 1.00
        }
    ]
    mock.rent_number.return_value = {
        "number": "+79001234567",
        "id": 12345678,
        "status": 1
    }
    mock.get_messages.return_value = [
        {
            "id": 1,
            "text": "Your verification code is 1234"
        }
    ]
    return mock


@pytest.fixture
def mock_proxy_service():
    """Create a mock proxy service for testing"""
    mock = Mock()
    mock.tariffs.return_value = {
        "7": {
            "code": 7,
            "country": "Russia",
            "price": 0.50
        }
    }
    return mock


@pytest.fixture
def mock_free_service():
    """Create a mock free service for testing"""
    mock = Mock()
    mock.get_countries.return_value = {
        "7": {
            "code": 7,
            "country": "Russia",
            "services": ["telegram", "whatsapp"]
        }
    }
    return mock


@pytest.fixture
def mock_rent_service():
    """Create a mock rent service for testing"""
    mock = Mock()
    mock.get_tariff.return_value = Mock(code=7)
    return mock


@pytest.fixture
def sample_api_key():
    """Return a sample API key for testing"""
    return "90b7beba2e36054e19ec87ec1855ca46"


@pytest.fixture
def sample_balance_data():
    """Return sample balance data for testing"""
    return {
        "balance": 150.75,
        "zbalance": 25.50,
        "income": 125.25
    }


@pytest.fixture
def sample_error_response():
    """Return sample error response for testing"""
    return {
        "error": "Test error",
        "code": 400,
        "message": "Bad request"
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom options"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers"""
    for item in items:
        # Add unit marker to tests that don't have integration marker
        if "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to integration tests
        if "integration" in item.keywords:
            item.add_marker(pytest.mark.slow)
