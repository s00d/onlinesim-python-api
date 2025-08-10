"""
Mock data for testing onlinesim.ru API
Located in tests/ folder for proper organization
"""

# Mock balance data examples
MOCK_BALANCE_RESPONSES = {
    "successful": {
        "balance": 150.75,
        "zbalance": 25.50,
        "income": 125.25
    },
    
    "empty": {},
    
    "partial": {
        "balance": 50.00,
        "income": 30.00
        # zbalance missing
    },
    
    "zero_balance": {
        "balance": 0.00,
        "zbalance": 0.00,
        "income": 0.00
    },
    
    "large_amounts": {
        "balance": 9999.99,
        "zbalance": 5000.00,
        "income": 4999.99
    },
    
    "negative_balance": {
        "balance": -15.50,
        "zbalance": 0.00,
        "income": -15.50
    }
}

# Mock error responses
MOCK_ERROR_RESPONSES = {
    "invalid_api_key": {
        "error": "Invalid API key",
        "code": 401,
        "message": "Authentication failed"
    },
    
    "rate_limit_exceeded": {
        "error": "Rate limit exceeded",
        "code": 429,
        "message": "Too many requests"
    },
    
    "server_error": {
        "error": "Internal server error",
        "code": 500,
        "message": "Something went wrong"
    },
    
    "network_error": {
        "error": "Connection failed",
        "code": 0,
        "message": "Network timeout"
    }
}

# Mock user profile data
MOCK_USER_PROFILE = {
    "profile": {
        "id": 12345,
        "name": "Test User",
        "username": "testuser",
        "email": "test@example.com",
        "apikey": "",
        "api_access": True,
        "locale": "en",
        "number_region": "7",
        "number_country": "7",
        "number_reject": [],
        "ugroup": 1,
        "verify": 1,
        "block": 0,
        "payment": {
            "payment": 100.00,
            "income": 75.00,
            "spent": 25.00,
            "now": 150.00
        }
    }
}

# Mock numbers data
MOCK_NUMBERS_RESPONSES = {
    "available_numbers": [
        {
            "number": "+79001234567",
            "country": 7,
            "service": "telegram",
            "price": 1.00,
            "count": 10
        },
        {
            "number": "+79001234568",
            "country": 7,
            "service": "whatsapp",
            "price": 2.00,
            "count": 5
        }
    ],
    
    "rented_number": {
        "status": 1,
        "extension": 0,
        "messages": [],
        "sum": "1.00",
        "country": 7,
        "checked_time": "2024-01-15 10:30:00",
        "number": "+79001234567",
        "rent": 1,
        "tzid": 12345678,
        "time": 86400,
        "days": 1,
        "hours": 24,
        "extend": {},
        "checked": False,
        "reload": 0,
        "day_extend": 0,
        "m_ext": False,
        "freeze": False
    }
}

# Mock messages data
MOCK_MESSAGES = [
    {
        "id": 1,
        "service": "telegram",
        "text": "Your verification code is: 123456",
        "code": "123456",
        "created_at": "2024-01-15 10:35:00"
    },
    {
        "id": 2,
        "service": "whatsapp",
        "text": "Code: 654321",
        "code": "654321",
        "created_at": "2024-01-15 10:40:00"
    }
]

# Helper function to create custom mock responses
def create_mock_response(data_type, **custom_fields):
    """
    Create a custom mock response by merging base data with custom fields
    
    Args:
        data_type (str): Type of response ('balance', 'profile', 'numbers', etc.)
        **custom_fields: Custom fields to override or add
    
    Returns:
        dict: Customized mock response
    """
    base_data = {}
    
    if data_type == "balance":
        base_data = MOCK_BALANCE_RESPONSES["successful"].copy()
    elif data_type == "profile":
        base_data = MOCK_USER_PROFILE["profile"].copy()
    elif data_type == "numbers":
        base_data = MOCK_NUMBERS_RESPONSES["available_numbers"][0].copy()
    elif data_type == "messages":
        base_data = MOCK_MESSAGES[0].copy()
    else:
        base_data = {}
    
    # Merge custom fields
    base_data.update(custom_fields)
    return base_data


# Mock factory for creating different types of mocks
class MockFactory:
    """Factory class for creating different types of mock objects"""
    
    @staticmethod
    def create_driver_mock():
        """Create a mock driver with all services"""
        mock_driver = Mock()
        mock_driver.user.return_value = MockFactory.create_user_service_mock()
        mock_driver.numbers.return_value = MockFactory.create_numbers_service_mock()
        mock_driver.proxy.return_value = MockFactory.create_proxy_service_mock()
        return mock_driver
    
    @staticmethod
    def create_user_service_mock():
        """Create a mock user service"""
        mock_user_service = Mock()
        mock_user_service.balance.return_value = MOCK_BALANCE_RESPONSES["successful"]
        mock_user_service.profile.return_value = MOCK_USER_PROFILE["profile"]
        return mock_user_service
    
    @staticmethod
    def create_numbers_service_mock():
        """Create a mock numbers service"""
        mock_numbers_service = Mock()
        mock_numbers_service.get_numbers.return_value = MOCK_NUMBERS_RESPONSES["available_numbers"]
        mock_numbers_service.rent_number.return_value = MOCK_NUMBERS_RESPONSES["rented_number"]
        mock_numbers_service.get_messages.return_value = MOCK_MESSAGES
        return mock_numbers_service
    
    @staticmethod
    def create_proxy_service_mock():
        """Create a mock proxy service"""
        mock_proxy_service = Mock()
        mock_proxy_service.get_proxies.return_value = []
        return mock_proxy_service
