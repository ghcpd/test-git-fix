# Minimal README for case_after

## Issue Description
The original test-suite contains tests that require network access and therefore fail in isolated environments (for example when building packages in a VM without network access).

The following tests were identified as requiring network access and are now marked with the `network` pytest marker:
- test_fake_user_agent*
- *update*
- *cache_server*
- test_utils_get*
- test_utils_load
- test_fake_default_path
- test_fake_safe_attrs

## Solution
Network-dependent tests are marked as `network`. You can skip them when running tests in an offline environment using:

```bash
# skip network tests
pytest -m "not network"
```

(Alternatively you can use name-based filtering: `pytest -k "not network"`, but using markers is more explicit.)

## Running Tests
```bash
cd case_after
pytest tests/
```