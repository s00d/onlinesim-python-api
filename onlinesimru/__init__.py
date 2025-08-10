# -*- coding: utf-8 -*-
import os
import re
from .services.free_numbers_service import FreeNumbersService
from .services.temp_numbers_service import NumbersService
from .services.proxy_service import ProxyService
from .services.rent_numbers_service import RentNumbersService
from .services.user_service import UserService
from .driver import Driver

# Читаем версию из pyproject.toml
def get_version():
    try:
        # Получаем путь к pyproject.toml
        # Ищем pyproject.toml в текущей директории или выше
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Поднимаемся вверх по дереву директорий, ища pyproject.toml
        while current_dir != os.path.dirname(current_dir):
            pyproject_path = os.path.join(current_dir, 'pyproject.toml')
            if os.path.exists(pyproject_path):
                with open(pyproject_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем строку version = "X.X.X"
                match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
                if match:
                    return match.group(1)
            
            current_dir = os.path.dirname(current_dir)
            
    except (FileNotFoundError, IOError, AttributeError, UnicodeDecodeError):
        pass
    
    # Fallback версия
    return "2.1.0"

__author__ = "s00d"
__version__ = get_version()
__contact__ = "https://github.com/s00d"
