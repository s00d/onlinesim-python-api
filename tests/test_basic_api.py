"""
Basic API tests for onlinesimru package
Tests basic functionality of the Driver class and its services
"""

import unittest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from onlinesimru import Driver


class TestBasicAPI(unittest.TestCase):
    """Basic API functionality tests"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Use a test API key for testing
        self.api_key = "90b7beba2e36054e19ec87ec1855ca46"
        self.driver = Driver(self.api_key)

    def test_free_service(self):
        """Test free service functionality"""
        # Act
        data = self.driver.free().get_countries()
        
        # Assert
        self.assertIsNotNone(data)
        # get_countries returns a list of countries, not a dict
        self.assertIsInstance(data, list)

    def test_numbers_service_tariffs(self):
        """Test numbers service tariffs functionality"""
        # Act
        data = self.driver.numbers().tariffs()
        
        # Assert
        self.assertIsNotNone(data)
        self.assertTrue('7' in data)

    def test_numbers_service_tariffs_one(self):
        """Test numbers service single tariff functionality"""
        # Act
        data = self.driver.numbers().tariffsOne(7)
        
        # Assert
        self.assertIsNotNone(data)
        self.assertEqual(data['code'], 7)

    def test_proxy_service_tariffs(self):
        """Test proxy service tariffs functionality"""
        # Act
        data = self.driver.proxy().tariffs()
        
        # Assert
        self.assertIsNotNone(data)
        self.assertEqual(data['response'], '1')

    def test_rent_service_tariff(self):
        """Test rent service tariff functionality"""
        # Act
        data = self.driver.rent().get_tariff()
        
        # Assert
        self.assertIsNotNone(data)
        self.assertTrue(data.code == 7)

    def test_user_service_balance(self):
        """Test user service balance functionality"""
        # Act
        data = self.driver.user().balance()
        
        # Assert
        self.assertIsNotNone(data)
        self.assertEqual(data['response'], '1')
        self.assertTrue('response' in data)
        self.assertTrue('balance' in data)
        self.assertTrue('income' in data)

    def test_api_key_validation(self):
        """Test that API key is properly set"""
        # Assert - use apikey instead of api_key
        self.assertEqual(self.driver.apikey, self.api_key)

    def test_driver_initialization(self):
        """Test driver initialization with different API keys"""
        # Test with empty API key
        driver_empty = Driver("")
        self.assertEqual(driver_empty.apikey, "")
        
        # Test with None API key
        driver_none = Driver(None)
        self.assertEqual(driver_none.apikey, None)


class TestAPIServiceStructure(unittest.TestCase):
    """Test the structure and availability of API services"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "90b7beba2e36054e19ec87ec1855ca46"
        self.driver = Driver(self.api_key)

    def test_service_availability(self):
        """Test that all expected services are available"""
        # Assert
        self.assertTrue(hasattr(self.driver, 'free'))
        self.assertTrue(hasattr(self.driver, 'numbers'))
        self.assertTrue(hasattr(self.driver, 'proxy'))
        self.assertTrue(hasattr(self.driver, 'rent'))
        self.assertTrue(hasattr(self.driver, 'user'))

    def test_service_methods_availability(self):
        """Test that service methods are callable"""
        # Assert
        self.assertTrue(callable(self.driver.free))
        self.assertTrue(callable(self.driver.numbers))
        self.assertTrue(callable(self.driver.proxy))
        self.assertTrue(callable(self.driver.rent))
        self.assertTrue(callable(self.driver.user))

    def test_service_return_types(self):
        """Test that services return proper objects"""
        # Act
        free_service = self.driver.free()
        numbers_service = self.driver.numbers()
        proxy_service = self.driver.proxy()
        rent_service = self.driver.rent()
        user_service = self.driver.user()
        
        # Assert
        self.assertIsNotNone(free_service)
        self.assertIsNotNone(numbers_service)
        self.assertIsNotNone(proxy_service)
        self.assertIsNotNone(rent_service)
        self.assertIsNotNone(user_service)


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2)
