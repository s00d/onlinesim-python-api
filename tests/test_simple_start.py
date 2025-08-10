"""
Tests for simple_start.py
Located in tests/ folder for proper Python package structure
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from example.simple_start import main


class TestSimpleStart(unittest.TestCase):
    """Test cases for simple_start.py with proper test structure"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # This method runs before each test
        self.mock_driver = Mock()
        self.mock_user_service = Mock()
        self.mock_driver.user.return_value = self.mock_user_service

    def tearDown(self):
        """Clean up after each test method"""
        # This method runs after each test
        pass

    @patch('example.simple_start.Driver')
    def test_successful_balance_retrieval(self, mock_driver_class):
        """Test successful balance retrieval with mock data"""
        # Arrange - prepare test data
        mock_driver_instance = Mock()
        mock_driver_class.return_value = mock_driver_instance
        
        mock_user_service = Mock()
        mock_driver_instance.user.return_value = mock_user_service
        
        # Mock successful API response
        mock_balance_data = {
            'balance': 100.50,
            'zbalance': 25.00,
            'income': 75.50
        }
        mock_user_service.balance.return_value = mock_balance_data
        
        # Act - execute the function under test
        with patch('builtins.print') as mock_print:
            main()
        
        # Assert - verify the results
        mock_driver_class.assert_called_once_with("")
        mock_driver_instance.user.assert_called_once()
        mock_user_service.balance.assert_called_once()
        
        # Check that balance data was printed correctly
        # Note: simple_start.py uses \n before "Full API response:", not separate print("")
        expected_calls = [
            unittest.mock.call("Balance data:"),
            unittest.mock.call("Balance: 100.5"),  # Python prints 100.50 as 100.5
            unittest.mock.call("Z-Balance: 25.0"),  # Python prints 25.00 as 25.0
            unittest.mock.call("Income: 75.5"),  # Python prints 75.50 as 75.5
            unittest.mock.call("\nFull API response:"),  # \n is part of the string, not separate print
            unittest.mock.call(mock_balance_data)
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)

    @patch('example.simple_start.Driver')
    def test_api_error_handling(self, mock_driver_class):
        """Test error handling when API call fails"""
        # Arrange
        mock_driver_instance = Mock()
        mock_driver_class.return_value = mock_driver_instance
        
        mock_user_service = Mock()
        mock_driver_instance.user.return_value = mock_user_service
        
        # Mock API error
        mock_user_service.balance.side_effect = Exception("API connection failed")
        
        # Act
        with patch('builtins.print') as mock_print:
            main()
        
        # Assert
        mock_driver_class.assert_called_once_with("")
        mock_user_service.balance.assert_called_once()
        
        # Check error messages were printed
        expected_error_calls = [
            unittest.mock.call("Error getting balance: API connection failed"),
            unittest.mock.call("API key might be required for this function")
        ]
        mock_print.assert_has_calls(expected_error_calls, any_order=False)

    @patch('example.simple_start.Driver')
    def test_empty_balance_data(self, mock_driver_class):
        """Test handling of empty or incomplete balance data"""
        # Arrange
        mock_driver_instance = Mock()
        mock_driver_class.return_value = mock_driver_instance
        
        mock_user_service = Mock()
        mock_driver_instance.user.return_value = mock_user_service
        
        # Mock incomplete API response
        mock_balance_data = {}
        mock_user_service.balance.return_value = mock_balance_data
        
        # Act
        with patch('builtins.print') as mock_print:
            main()
        
        # Assert
        mock_user_service.balance.assert_called_once()
        
        # Check that N/A values are displayed for missing data
        expected_calls = [
            unittest.mock.call("Balance data:"),
            unittest.mock.call("Balance: N/A"),
            unittest.mock.call("Z-Balance: N/A"),
            unittest.mock.call("Income: N/A"),
            unittest.mock.call("\nFull API response:"),  # \n is part of the string
            unittest.mock.call(mock_balance_data)
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)

    @patch('example.simple_start.Driver')
    def test_partial_balance_data(self, mock_driver_class):
        """Test handling of partial balance data"""
        # Arrange
        mock_driver_instance = Mock()
        mock_driver_class.return_value = mock_driver_instance
        
        mock_user_service = Mock()
        mock_driver_instance.user.return_value = mock_user_service
        
        # Mock partial API response
        mock_balance_data = {
            'balance': 50.00,
            # 'zbalance' missing
            'income': 30.00
        }
        mock_user_service.balance.return_value = mock_balance_data
        
        # Act
        with patch('builtins.print') as mock_print:
            main()
        
        # Assert
        mock_user_service.balance.assert_called_once()
        
        # Check that available data is displayed and missing data shows N/A
        expected_calls = [
            unittest.mock.call("Balance data:"),
            unittest.mock.call("Balance: 50.0"),  # Python prints 50.00 as 50.0
            unittest.mock.call("Z-Balance: N/A"),
            unittest.mock.call("Income: 30.0"),  # Python prints 30.00 as 30.0
            unittest.mock.call("\nFull API response:"),  # \n is part of the string
            unittest.mock.call(mock_balance_data)
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)


class TestSimpleStartEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    @patch('example.simple_start.Driver')
    def test_zero_balance_values(self, mock_driver_class):
        """Test handling of zero balance values"""
        # Arrange
        mock_driver_instance = Mock()
        mock_driver_class.return_value = mock_driver_instance
        
        mock_user_service = Mock()
        mock_driver_instance.user.return_value = mock_user_service
        
        mock_balance_data = {
            'balance': 0.00,
            'zbalance': 0.00,
            'income': 0.00
        }
        mock_user_service.balance.return_value = mock_balance_data
        
        # Act
        with patch('builtins.print') as mock_print:
            main()
        
        # Assert
        expected_calls = [
            unittest.mock.call("Balance data:"),
            unittest.mock.call("Balance: 0.0"),  # Python prints 0.00 as 0.0
            unittest.mock.call("Z-Balance: 0.0"),  # Python prints 0.00 as 0.0
            unittest.mock.call("Income: 0.0"),  # Python prints 0.00 as 0.0
            unittest.mock.call("\nFull API response:"),  # \n is part of the string
            unittest.mock.call(mock_balance_data)
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)

    @patch('example.simple_start.Driver')
    def test_large_balance_values(self, mock_driver_class):
        """Test handling of large balance values"""
        # Arrange
        mock_driver_instance = Mock()
        mock_driver_class.return_value = mock_driver_instance
        
        mock_user_service = Mock()
        mock_driver_instance.user.return_value = mock_user_service
        
        mock_balance_data = {
            'balance': 999999.99,
            'zbalance': 500000.00,
            'income': 499999.99
        }
        mock_user_service.balance.return_value = mock_balance_data
        
        # Act
        with patch('builtins.print') as mock_print:
            main()
        
        # Assert
        expected_calls = [
            unittest.mock.call("Balance data:"),
            unittest.mock.call("Balance: 999999.99"),  # Large numbers keep precision
            unittest.mock.call("Z-Balance: 500000.0"),  # Python prints 500000.00 as 500000.0
            unittest.mock.call("Income: 499999.99"),  # Large numbers keep precision
            unittest.mock.call("\nFull API response:"),  # \n is part of the string
            unittest.mock.call(mock_balance_data)
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2)
