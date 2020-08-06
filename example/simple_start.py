from onlinesimru import GetFree, GetForward, GetUser

def main():
    client = GetFree('')
    countries = client.countries()
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
