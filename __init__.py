# Package wrapper for the original tests defined in case_before.py.
# This package exposes the same test symbols while allowing the
# directory-style import requested by packaging and test harnesses.

from __future__ import annotations

# Re-export everything from the original module so test discovery sees
# the same functions and names.
from case_before import *  # noqa: F401,F403

import socket
import pytest
import types
from typing import Callable


def _network_available(timeout: float = 0.8) -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout).close()
        return True
    except Exception:
        return False


_NET_PATTERNS = (
    "fake_user_agent",
    "update",
    "cache_server",
    "utils_get",
    "utils_load",
    "fake_default_path",
    "fake_safe_attrs",
)


def _should_tag_for_network(name: str) -> bool:
    name = name.lower()
    if not name.startswith("test_"):
        return False
    return any(pat in name for pat in _NET_PATTERNS)


def _decorate_network_tests(ns: dict):
    network_up = _network_available()
    reason = (
        "requires network — running in isolated environment so test is skipped"
        if not network_up
        else "requires network"
    )

    for name, value in list(ns.items()):
        if not _should_tag_for_network(name):
            continue
        if not isinstance(value, types.FunctionType):
            continue

        m = pytest.mark.network
        skip_on_isolated = pytest.mark.skipif(not network_up, reason=reason)
        decorated = m(skip_on_isolated(value))
        ns[name] = decorated


_decorate_network_tests(globals())


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "network: marks tests that require outbound network access and can be "
        "skipped in isolated environments",
    )
