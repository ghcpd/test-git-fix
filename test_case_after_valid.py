import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
AFTER = HERE / "case_after.py"
BEFORE = HERE / "case_before.py"


def test_case_after_exists_and_contains_network_marks():
    import importlib, importlib.util
    importlib.invalidate_caches()
    # case_after should be a package directory
    pkg_dir = BEFORE.parent / "case_after"
    assert pkg_dir.exists() and pkg_dir.is_dir(), "case_after must be a package directory (case_after/)"
    # Import the package which will re-export all symbols and add marks
    import case_after as mod
    assert hasattr(mod, "_marked_tests"), "case_after package must expose _marked_tests()"
    marked_list = mod._marked_tests()
    assert marked_list, "case_after must mark at least one test as network-only"
    # Verify at least one of the canonical tokens is present as a marked test
    tokens = ("test_fake_user_agent", "test_utils_get", "test_utils_load", "test_fake_default_path", "test_fake_safe_attrs")
    ok = any(any(token in name for name in marked_list) for token in tokens)
    assert ok, "expected at least one network-marked test matching the issue list"
    # Finally, verify running pytest -k 'not network' would skip at least the marked tests
    # (we cannot run pytest inside the unit but it's enough that functions have pytestmark)
    for name in marked_list:
        obj = getattr(mod, name, None)
        assert obj is not None and getattr(obj, "pytestmark", None), f"marked test {name} must still have pytestmark on it"


