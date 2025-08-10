import pytest
from unittest.mock import patch, Mock
from onlinesimru.api import API
from onlinesimru import Driver


class TestCustomDomain:
    """Тесты для функциональности кастомного домена"""
    
    def test_api_custom_domain(self):
        """Тест создания API с кастомным доменом"""
        custom_url = "https://custom-api.com"
        api = API(base_url=custom_url)
        
        assert api.base_url == custom_url
        assert api.base_url == "https://custom-api.com"
    
    def test_api_custom_domain_with_trailing_slash(self):
        """Тест создания API с кастомным доменом с trailing slash"""
        custom_url = "https://custom-api.com/"
        api = API(base_url=custom_url)
        
        assert api.base_url == "https://custom-api.com"
    
    def test_api_default_domain(self):
        """Тест создания API с доменом по умолчанию"""
        api = API()
        
        assert api.base_url == "https://onlinesim.host"
    
    def test_driver_custom_domain(self):
        """Тест создания Driver с кастомным доменом"""
        custom_url = "https://custom-api.com"
        driver = Driver("", base_url=custom_url)
        
        assert driver.base_url == custom_url
    
    @patch('httpx.get')
    def test_api_get_with_custom_domain(self, mock_get):
        """Тест GET запроса с кастомным доменом"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "1", "data": "test"}
        mock_get.return_value = mock_response
        
        custom_url = "https://custom-api.com"
        api = API(base_url=custom_url)
        
        result = api._get("/test")
        
        # Проверяем, что запрос был сделан на правильный URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://custom-api.com/api/test.php"
        
        assert result == {"response": "1", "data": "test"}
    
    @patch('httpx.post')
    def test_api_post_with_custom_domain(self, mock_post):
        """Тест POST запроса с кастомным доменом"""
        mock_response = Mock()
        mock_response.json.return_value = {"response": "1", "data": "test"}
        mock_post.return_value = mock_response
        
        custom_url = "https://custom-api.com"
        api = API(base_url=custom_url)
        
        result = api._post("/test")
        
        # Проверяем, что запрос был сделан на правильный URL
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://custom-api.com/api/test.php"
        
        assert result == {"response": "1", "data": "test"}
    
    def test_driver_services_inherit_base_url(self):
        """Тест что все сервисы Driver наследуют base_url"""
        custom_url = "https://custom-api.com"
        driver = Driver("", base_url=custom_url)
        
        # Проверяем что все сервисы имеют доступ к base_url
        assert driver.user().base_url == custom_url
        assert driver.numbers().base_url == custom_url
        assert driver.free().base_url == custom_url
        assert driver.proxy().base_url == custom_url
        assert driver.rent().base_url == custom_url
