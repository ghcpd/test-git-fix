import os
import urllib
from unittest.mock import patch
import unittest
import pytest
from fake_useragent import UserAgent, FakeUserAgentError, settings


class TestFake(unittest.TestCase):
    def setUp(self):
        try:
            os.remove(settings.DB)
        except OSError:
            pass

    def tearDown(self):
        try:
            os.remove(settings.DB)
        except OSError:
            pass

    def test_fake_user_agent_browsers(self):
        """This test no longer requires network - uses local data"""
        ua = UserAgent()  # Default uses local data, no network access
        
        self.assertTrue(ua.chrome)
        self.assertIsInstance(ua.chrome, str)

    def test_fake_default_path(self):
        """This test no longer requires network - uses local data with mock"""
        assert not os.path.isfile(settings.DB)
        
        # Mock to avoid actual network call if use_external_data=True
        with patch.object(urllib.request, "urlopen"):
            ua = UserAgent()  # Uses local data by default
        
        # Note: path renamed to cache_path in new API
        assert settings.DB == ua.cache_path

    def test_fake_update(self):
        """This test no longer requires network - uses local data"""
        ua = UserAgent()  # Uses local data
        
        # Will not do much by default, just reload local data
        ua.update()
        
        self.assertTrue(ua.chrome)

    def test_fake_safe_attrs(self):
        """This test no longer requires network - uses local data"""
        ua = UserAgent(safe_attrs=("__injections__",))
        
        with pytest.raises(AttributeError):
            ua.__injections__
