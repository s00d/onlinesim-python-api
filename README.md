# Onlinesim Python API


Wrapper for automatic reception of SMS-messages by onlinesim.ru

[![N|Solid](https://img.shields.io/pypi/pyversions/onlinesimru.svg)](https://pypi.python.org/pypi/onlinesimru)

### Installation
You can install or upgrade package with:
```
$ pip install onlinesimru --upgrade
```
Or you can install from source with:
```
$ git clone https://github.com/s00d/onlinesim-python-api
$ cd onlinesim-python-api
$ python setup.py install
```
...or install from source buth with pip
```
$ pip install git+https://github.com/s00d/onlinesim-python-api
```
### Example
```python
from onlinesimru import GetFree, GetRent, GetProxy, GetForward, GetUser, GetNumbers

def main():
    client = GetUser('YOUR_TOKEN')
    balance = client.balance()
    print(balance)

main()
```

### Example2
```python
from onlinesimru import GetFree, GetRent, GetProxy, GetForward, GetUser, GetNumbers

def main():
    numbers = GetNumbers('YOUR_TOKEN')
    input('Press enter if you sms was sent')

    tzid = numbers.get('service')
    print(tzid)
    code = numbers.wait_code(tzid)
    print(code)

main()
```

### Example3
```python
# multiple driver using
from onlinesimru import Driver

def main():
    driver = Driver('YOUR_TOKEN')

    tzid = driver.numbers().get('service')
    print(tzid)
    code = driver.numbers().wait_code(tzid)
    print(code)

main()
```

## Documentation

All documentation is in the wiki of this project - **[Documentation](https://github.com/s00d/onlinesim-python-api/wiki)**

## Bugs

If you have any problems, please create Issues [here](https://github.com/s00d/onlinesim-python-api/issues)  
