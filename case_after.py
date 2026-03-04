# Shim to keep both 'import case_after' and 'import case_after.__init__' working
# while also providing a package-style corrected copy (case_after/.__init__.py).
import importlib
import pkgutil

# Ensure the package is importable (importing the package will run the
# 'complete copy' logic that marks networked tests).
import case_after as _pkg  # noqa: F401  (the package lives in case_after/__init__.py)

# Re-export to make this top-level file behave as the package module
__all__ = getattr(_pkg, "__all__", [])

# Forward _marked_tests helper if present
try:
    _marked_tests = _pkg._marked_tests  # type: ignore
except Exception:
    pass

print('case_after shim loaded; use the package "case_after" (directory) for the fixed copy')


