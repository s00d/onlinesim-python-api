# Onlinesim Python API

Wrapper for automatic reception of SMS-messages by onlinesim.ru

[![N|Solid](https://img.shields.io/pypi/pyversions/onlinesimru.svg)](https://pypi.python.org/pypi/onlinesimru)
![Publish to PyPI](https://github.com/s00d/onlinesim-python-api/workflows/Publish%20to%20PyPI/badge.svg)

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
from onlinesimru import FreeNumbersService, RentNumbersService, ProxyService, UserService, NumbersService


def main():
    client = UserService('YOUR_TOKEN')
    balance = client.balance()
    print(balance)


main()
```

### Example2

```python
from onlinesimru import FreeNumbersService, RentNumbersService, ProxyService, UserService, NumbersService


def main():
    numbers = NumbersService('YOUR_TOKEN')
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

### Example4 - Custom Domain

```python
# Using custom domain for API endpoints
from onlinesimru import Driver


def main():
    # Use custom domain
    driver = Driver('YOUR_TOKEN', base_url='https://custom-onlinesim.com')
    
    # Or use local development server
    driver_local = Driver('YOUR_TOKEN', base_url='http://localhost:8000')
    
    # Standard usage remains the same
    tzid = driver.numbers().get('service')
    print(tzid)


main()
```

## Documentation

All documentation is in the wiki of this project - **[Documentation](https://github.com/s00d/onlinesim-python-api/wiki)**

## Testing

The project includes comprehensive test coverage. All tests are located in the `tests/` directory.

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_basic_api.py -v
python -m pytest tests/integration_tests.py -v

# Run tests with coverage
python -m pytest tests/ --cov=onlinesimru --cov-report=html
```

For more detailed testing information, see [tests/README.md](tests/README.md).

## Bugs

If you have any problems, please create Issues [here](https://github.com/s00d/onlinesim-python-api/issues)  
