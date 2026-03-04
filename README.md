# Minimal README for case_before

## Issue Description
When the tests are run in an isolated VM (such as used for distro packaging), the following tests fail trying to reach the network:
- test_fake_user_agent*
- *update*
- *cache_server*
- test_utils_get*
- test_utils_load
- test_fake_default_path
- test_fake_safe_attrs

## Problem
Tests depend on network access via `cache=False, use_cache_server=False` parameters.

## Running Tests
```bash
cd case_before
pytest tests/
```

Expected: Tests will fail in isolated environment without network access.
