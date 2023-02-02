from onlinesimru import Driver


def main():
    driver = Driver("")
    data = driver.temp_numbers().wait_code(tzid=23583470, timeout=1)
    print(data)
    # numbers = client.numbers(7)
    # print(numbers)

    # messages = client.messages(9651622343)
    # print(messages)

    # client = GetUser('111111')
    # balance = client.balance()
    # print(balance)


main()
