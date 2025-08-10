# Тесты для onlinesim-python-api

Эта папка содержит все тесты для проекта onlinesim-python-api.

## Структура тестов

- **`test_simple_start.py`** - Тесты для примера simple_start.py
- **`test_basic_api.py`** - Базовые тесты API функциональности
- **`integration_tests.py`** - Интеграционные тесты с использованием mock данных
- **`mock_data_examples.py`** - Mock данные для тестирования
- **`conftest.py`** - Конфигурация pytest и общие фикстуры
- **`__init__.py`** - Инициализация пакета тестов

## Установка зависимостей

```bash
pip install pytest pytest-cov pytest-mock
```

## Запуск тестов

### Запуск всех тестов
```bash
python -m pytest tests/ -v
```

### Запуск конкретного файла тестов
```bash
python -m pytest tests/test_simple_start.py -v
python -m pytest tests/test_basic_api.py -v
python -m pytest tests/integration_tests.py -v
```

### Запуск тестов с покрытием кода
```bash
python -m pytest tests/ --cov=onlinesimru --cov-report=html
```

### Запуск только unit тестов (быстрые)
```bash
python -m pytest tests/ -m unit -v
```

### Запуск только integration тестов (медленные)
```bash
python -m pytest tests/ -m integration -v
```

### Запуск тестов без предупреждений
```bash
python -m pytest tests/ -v --disable-warnings
```

## Маркеры тестов

- `@pytest.mark.unit` - Unit тесты (быстрые)
- `@pytest.mark.integration` - Интеграционные тесты (медленные)
- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.api` - API связанные тесты
- `@pytest.mark.mock` - Тесты с mock данными

## Фикстуры

В `conftest.py` определены общие фикстуры:

- `mock_driver` - Mock экземпляр Driver
- `mock_user_service` - Mock сервис пользователя
- `mock_numbers_service` - Mock сервис номеров
- `mock_proxy_service` - Mock сервис прокси
- `sample_api_key` - Пример API ключа
- `sample_balance_data` - Пример данных баланса

## Пример использования фикстур

```python
def test_balance_check(mock_driver, mock_user_service):
    # Настройка mock
    mock_driver.user.return_value = mock_user_service
    
    # Выполнение теста
    result = mock_driver.user().balance()
    
    # Проверки
    assert result["balance"] == 100.00
```

## Mock данные

В `mock_data_examples.py` содержатся различные mock данные:

- Баланс пользователя
- Ошибки API
- Профиль пользователя
- Номера телефонов
- Сообщения
- Прокси
- Тарифы

## Добавление новых тестов

1. Создайте новый файл с префиксом `test_`
2. Наследуйтесь от `unittest.TestCase` или используйте pytest
3. Добавьте соответствующие маркеры
4. Используйте существующие фикстуры или создайте новые

## Troubleshooting

### Ошибка импорта модулей
Убедитесь, что в тестах правильно настроен путь к проекту:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

### Тесты не запускаются
Проверьте, что установлен pytest:
```bash
pip install pytest
```

### Mock данные не работают
Убедитесь, что импортируете mock данные из правильного места:
```python
from mock_data_examples import MOCK_BALANCE_RESPONSES
```
