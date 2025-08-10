"""
Mock data examples for onlinesim.ru API testing
This file contains sample data structures that mimic real API responses
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
            "count": 5
        },
        {
            "number": "+79001234568",
            "country": 7,
            "service": "whatsapp",
            "price": 1.50,
            "count": 3
        }
    ],
    
    "rented_number": {
        "number": "+79001234567",
        "id": 12345678,
        "country": 7,
        "service": "telegram",
        "price": 1.00,
        "status": 1,
        "rented_at": "2024-01-15 10:30:00",
        "expires_at": "2024-01-16 10:30:00"
    },
    
    "number_status": {
        "id": 12345678,
        "number": "+79001234567",
        "status": 1,
        "message_count": 2,
        "last_message": "2024-01-15 15:45:00"
    }
}

# Mock messages data
MOCK_MESSAGES = [
    {
        "id": 1,
        "number": "+79001234567",
        "text": "Your verification code is 1234",
        "received_at": "2024-01-15 15:30:00",
        "service": "telegram"
    },
    {
        "id": 2,
        "number": "+79001234567",
        "text": "Welcome to our service!",
        "received_at": "2024-01-15 15:45:00",
        "service": "telegram"
    }
]

# Mock proxy data
MOCK_PROXY_RESPONSES = {
    "proxy_tariffs": {
        "7": {
            "code": 7,
            "country": "Russia",
            "price": 0.50,
            "currency": "USD",
            "type": "http"
        },
        "1": {
            "code": 1,
            "country": "USA",
            "price": 1.00,
            "currency": "USD",
            "type": "http"
        }
    },
    
    "proxy_rental": {
        "id": 98765,
        "ip": "192.168.1.100",
        "port": 8080,
        "country": 7,
        "type": "http",
        "username": "proxy_user",
        "password": "proxy_pass",
        "expires_at": "2024-01-16 10:30:00"
    }
}

# Mock rent data
MOCK_RENT_RESPONSES = {
    "rent_tariff": {
        "code": 7,
        "country": "Russia",
        "price": 2.00,
        "currency": "USD",
        "type": "rent",
        "duration": 24
    },
    
    "rented_number": {
        "id": 12345678,
        "number": "+79001234567",
        "country": 7,
        "service": "telegram",
        "price": 2.00,
        "status": 1,
        "rented_at": "2024-01-15 10:30:00",
        "expires_at": "2024-01-16 10:30:00"
    }
}

# Mock free service data
MOCK_FREE_RESPONSES = {
    "countries": {
        "7": {
            "code": 7,
            "country": "Russia",
            "services": ["telegram", "whatsapp", "viber"],
            "available_numbers": 15
        },
        "1": {
            "code": 1,
            "country": "USA",
            "services": ["telegram", "whatsapp"],
            "available_numbers": 8
        }
    },
    
    "numbers": [
        {
            "number": "+79001234567",
            "country": 7,
            "service": "telegram",
            "status": "available"
        },
        {
            "number": "+79001234568",
            "country": 7,
            "service": "whatsapp",
            "status": "available"
        }
    ]
}

# Mock API response structure
MOCK_API_RESPONSE = {
    "response": "1",
    "data": {},
    "error": None,
    "timestamp": "2024-01-15 10:30:00"
}

# Mock pagination data
MOCK_PAGINATION = {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
}

# Mock statistics data
MOCK_STATISTICS = {
    "total_numbers": 150,
    "rented_numbers": 45,
    "available_numbers": 105,
    "total_income": 1250.75,
    "monthly_income": 125.50
}

# Utility function to create custom mock responses
def create_mock_response(data, status_code=200, message="Success"):
    """
    Create a custom mock response with specified data
    
    Args:
        data: The response data
        status_code: HTTP status code
        message: Response message
        
    Returns:
        dict: Mock response structure
    """
    return {
        "data": data,
        "status": status_code,
        "message": message,
        "timestamp": "2024-01-15 10:30:00"
    }

# Mock validation data
MOCK_VALIDATION = {
    "valid_api_key": "90b7beba2e36054e19ec87ec1855ca46",
    "invalid_api_key": "invalid_key_123",
    "empty_api_key": "",
    "null_api_key": None
}

# Mock configuration data
MOCK_CONFIG = {
    "base_url": "https://onlinesim.ru/api",
    "timeout": 30,
    "retry_attempts": 3,
    "rate_limit": 100,
    "rate_limit_window": 3600
}

# Mock error scenarios for testing
MOCK_ERROR_SCENARIOS = {
    "timeout": {
        "error": "Request timeout",
        "code": 408,
        "message": "Request timed out after 30 seconds"
    },
    "invalid_request": {
        "error": "Invalid request",
        "code": 400,
        "message": "Bad request format"
    },
    "unauthorized": {
        "error": "Unauthorized",
        "code": 401,
        "message": "Access denied"
    },
    "forbidden": {
        "error": "Forbidden",
        "code": 403,
        "message": "Access forbidden"
    },
    "not_found": {
        "error": "Not found",
        "code": 404,
        "message": "Resource not found"
    },
    "method_not_allowed": {
        "error": "Method not allowed",
        "code": 405,
        "message": "HTTP method not allowed"
    },
    "conflict": {
        "error": "Conflict",
        "code": 409,
        "message": "Resource conflict"
    },
    "unprocessable_entity": {
        "error": "Unprocessable entity",
        "code": 422,
        "message": "Validation failed"
    },
    "too_many_requests": {
        "error": "Too many requests",
        "code": 429,
        "message": "Rate limit exceeded"
    },
    "internal_server_error": {
        "error": "Internal server error",
        "code": 500,
        "message": "Server error occurred"
    },
    "bad_gateway": {
        "error": "Bad gateway",
        "code": 502,
        "message": "Bad gateway"
    },
    "service_unavailable": {
        "error": "Service unavailable",
        "code": 503,
        "message": "Service temporarily unavailable"
    },
    "gateway_timeout": {
        "error": "Gateway timeout",
        "code": 504,
        "message": "Gateway timeout"
    }
}
