from onlinesimru import FreeNumbersService, TempNumbersService, ProxyService, RentNumbersService, UserService
from .api import API


class Driver(API):
    def free(self):
        return FreeNumbersService(self.apikey, self.lang, self.lang)

    def temp_numbers(self):
        return TempNumbersService(self.apikey, self.lang, self.lang)

    def proxy(self):
        return ProxyService(self.apikey, self.lang, self.lang)

    def rent(self):
        return RentNumbersService(self.apikey, self.lang, self.lang)

    def user(self):
        return UserService(self.apikey, self.lang, self.lang)
