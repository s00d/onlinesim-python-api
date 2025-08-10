from onlinesimru import Driver


def main():
    # Create driver instance (you can pass API key if available)
    driver = Driver("")
    
    # Get user balance
    try:
        balance_data = driver.user().balance()
        print("Balance data:")
        print(f"Balance: {balance_data.get('balance', 'N/A')}")
        print(f"Z-Balance: {balance_data.get('zbalance', 'N/A')}")
        print(f"Income: {balance_data.get('income', 'N/A')}")
        
        # Print full API response for debugging
        print("\nFull API response:")
        print(balance_data)
        
    except Exception as e:
        print(f"Error getting balance: {e}")
        print("API key might be required for this function")


if __name__ == "__main__":
    main()
