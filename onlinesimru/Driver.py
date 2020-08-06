from onlinesimru import GetForward, GetFree, GetNumbers, GetProxy, GetRent, GetUser
from .api import Api


class Driver(Api):
    def forward(self):
        return GetForward(self.apikey, self.lang, self.lang)

    def free(self):
        return GetFree(self.apikey, self.lang, self.lang)

    def numbers(self):
        return GetNumbers(self.apikey, self.lang, self.lang)

    def proxy(self):
        return GetProxy(self.apikey, self.lang, self.lang)

    def rent(self):
        return GetRent(self.apikey, self.lang, self.lang)

    def user(self):
        return GetUser(self.apikey, self.lang, self.lang)