# A tiny shim to allow `case_after` to be a package directory while
# remaining importable if this file is kept in the tree.  The real
# implementation lives in the `case_after` package directory
# (case_after/__init__.py).

from importlib import import_module

_package = import_module("case_after")

# Re-export the package symbols so `from case_after import *` keeps
# behaving as before when tests import this module directly.
for _k, _v in vars(_package).items():
    if not _k.startswith("__"):
        globals()[_k] = _v

__all__ = [k for k in vars(_package) if not k.startswith("__")]
