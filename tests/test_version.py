"""
Тест для проверки функции get_version()
"""
import sys
import os

# Добавляем путь к модулю onlinesimru
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from onlinesimru import __version__


def test_version_format():
    """Тест что версия имеет правильный формат"""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0

    # Проверяем формат версии (например, 2.1.0)
    version_parts = __version__.split('.')
    assert len(version_parts) >= 2

    # Проверяем что все части - числа
    for part in version_parts:
        assert part.isdigit()


def test_version_value():
    """Тест что версия соответствует ожидаемой"""
    # Версия должна быть 2.1.0 или выше
    assert __version__ >= "2.1.0"


if __name__ == "__main__":
    print(f"Текущая версия: {__version__}")
    test_version_format()
    test_version_value()
    print("Все тесты прошли успешно!")