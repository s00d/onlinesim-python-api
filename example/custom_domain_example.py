from onlinesimru import Driver


def main():
    # Пример использования с кастомным доменом
    # Можно использовать для тестирования, зеркал или альтернативных API endpoints
    
    # Использование стандартного домена (по умолчанию)
    driver_default = Driver("")
    print("Используется стандартный домен: https://onlinesim.host")
    
    # Использование кастомного домена
    driver_custom = Driver("", base_url="https://custom-onlinesim.com")
    print("Используется кастомный домен: https://custom-onlinesim.com")
    
    # Использование локального домена для разработки
    driver_local = Driver("", base_url="http://localhost:8000")
    print("Используется локальный домен: http://localhost:8000")
    
    # Пример с API ключом и кастомным доменом
    driver_with_key = Driver("your_api_key_here", base_url="https://api.onlinesim.ru")
    print("Используется API ключ с кастомным доменом: https://api.onlinesim.ru")
    
    # Получение баланса (работает с любым доменом)
    try:
        balance_data = driver_default.user().balance()
        print(f"\nБаланс (стандартный домен): {balance_data.get('balance', 'N/A')}")
        
        # Примечание: для кастомных доменов нужно убедиться, что API endpoint доступен
        print("\nПримечание: Кастомные домены должны иметь тот же API endpoint")
        print("Формат: {base_url}/api{endpoint}.php")
        
    except Exception as e:
        print(f"Ошибка при получении баланса: {e}")


if __name__ == "__main__":
    main()
