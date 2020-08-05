from onlinesimru import GetFree
import asyncio


async def main():
    client = GetFree('')
    countries = await client.countries()
    print(countries)
    numbers = await client.numbers(7)
    print(numbers)

asyncio.run(main())
