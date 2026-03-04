import random
from fake_useragent import settings
from fake_useragent.errors import FakeUserAgentError


class FakeUserAgent:
    def __init__(
        self,
        cache=True,
        use_cache_server=True,
        fallback=None,
    ):
        self.cache = cache
        self.use_cache_server = use_cache_server
        self.fallback = fallback
        self.data_browsers = {}
        self.load()

    def load(self):
        # Simulate loading from network
        if not self.use_cache_server:
            raise FakeUserAgentError("Network unavailable")
        self.data_browsers = {"chrome": ["Mozilla/5.0 Chrome/1.0"]}

    def update(self):
        self.load()

    @property
    def chrome(self):
        if not self.data_browsers:
            if self.fallback:
                return self.fallback
            raise FakeUserAgentError("No data")
        return random.choice(self.data_browsers.get("chrome", [self.fallback]))


UserAgent = FakeUserAgent
