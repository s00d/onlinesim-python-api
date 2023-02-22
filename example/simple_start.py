from onlinesimru import Driver


def main():
    driver = Driver("cbdbaabd86197f20c99805e21a413fe5")
    data = driver.numbers().wait_code(tzid=3014928, timeout=1)
    print(data)
    # numbers = client.numbers(7)
    # print(numbers)

    # messages = client.messages(9651622343)
    # print(messages)

    # client = GetUser('111111')
    # balance = client.balance()
    # print(balance)


main()
