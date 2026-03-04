import os
import tempfile

__version__ = "0.1.14"

DB = os.path.join(tempfile.gettempdir(), "fake_useragent_0.1.14.json")
CACHE_SERVER = "https://fake-useragent.herokuapp.com/browsers/0.1.11"
