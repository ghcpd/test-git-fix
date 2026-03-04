import random
import json
import os
from fake_useragent import settings
from fake_useragent.errors import FakeUserAgentError


class FakeUserAgent:
    def __init__(
        self,
        use_external_data=False,
        cache_path=settings.DB,
        fallback=None,
    ):
        self.use_external_data = use_external_data
        self.cache_path = cache_path
        self.fallback = fallback
        self.data_browsers = {}
        self.load()

    def load(self):
        # Load from local file by default (no network access)
        if self.use_external_data:
            # This would access network
            raise FakeUserAgentError("Network access required")
        else:
            # Load from local browsers.json
            try:
                data_dir = os.path.join(os.path.dirname(__file__), "data")
                browsers_file = os.path.join(data_dir, "browsers.json")
                with open(browsers_file, "r") as f:
                    self.data_browsers = json.load(f)
            except:
                if self.fallback:
                    self.data_browsers = {"chrome": [self.fallback]}
                else:
                    raise FakeUserAgentError("Cannot load data")

    def update(self, use_external_data=None):
        if use_external_data is not None:
            self.use_external_data = use_external_data
        self.load()

    @property
    def chrome(self):
        if not self.data_browsers:
            if self.fallback:
                return self.fallback
            raise FakeUserAgentError("No data")
        return random.choice(self.data_browsers.get("chrome", [self.fallback]))


UserAgent = FakeUserAgent
