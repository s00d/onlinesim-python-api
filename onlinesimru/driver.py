from onlinesimru import FreeNumbersService, NumbersService, ProxyService, RentNumbersService, UserService
from .api import API


class Driver(API):
    def free(self):
        return FreeNumbersService(self.apikey, self.lang, self.lang, self.base_url)

    def numbers(self):
        return NumbersService(self.apikey, self.lang, self.lang, self.base_url)

    def proxy(self):
        return ProxyService(self.apikey, self.lang, self.lang, self.base_url)

    def rent(self):
        return RentNumbersService(self.apikey, self.lang, self.lang, self.base_url)

    def user(self):
        return UserService(self.apikey, self.lang, self.lang, self.base_url)
