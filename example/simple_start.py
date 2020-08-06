from onlinesimru import Driver

def main():
    driver = Driver('')
    countries = driver.free().countries()
    print(countries)
    # numbers = client.numbers(7)
    # print(numbers)

    # messages = client.messages(9651622343)
    # print(messages)

    # client = GetForward('111111')
    # service = client.service()
    # print(service)

    # client = GetUser('111111')
    # balance = client.balance()
    # print(balance)

main()
