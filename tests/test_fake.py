import os
import pytest
from fake_useragent import UserAgent, FakeUserAgentError, settings


def setup_function(function):
    try:
        os.remove(settings.DB)
    except OSError:
        pass


def teardown_function(function):
    try:
        os.remove(settings.DB)
    except OSError:
        pass


@pytest.mark.network
def test_fake_user_agent_browsers():
    """This test requires network access and will fail in isolated environment"""
    ua = UserAgent(cache=False, use_cache_server=False)
    
    assert ua.chrome


@pytest.mark.network
def test_fake_default_path():
    """This test requires network access and will fail in isolated environment"""
    assert not os.path.isfile(settings.DB)
    
    ua = UserAgent(cache=True, use_cache_server=False)
    
    assert settings.DB == ua.path
    assert os.path.isfile(settings.DB)


@pytest.mark.network
def test_fake_update():
    """This test requires network access and will fail in isolated environment"""
    ua = UserAgent(cache=False, use_cache_server=False)
    
    ua.update()
    
    assert ua.chrome


@pytest.mark.network
def test_fake_safe_attrs():
    """This test requires network access and will fail in isolated environment"""
    ua = UserAgent(safe_attrs=("__injections__",))
    
    with pytest.raises(AttributeError):
        ua.__injections__
