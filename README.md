# Minimal README for case_after

## Fix Description
Tests no longer require network access. The fix includes:

1. **API Change**: Changed from `cache=False, use_cache_server=False` to `use_external_data=False` (default)
2. **Local Data**: Added local `browsers.json` file with user agent strings
3. **Default Behavior**: By default, uses local file instead of accessing network
4. **Test Updates**: Tests use local data and mocks to avoid network dependency

## Key Changes
- `fake_useragent/fake.py`: New `use_external_data` parameter replaces network-dependent parameters
- `fake_useragent/data/browsers.json`: Local user agent data file
- `tests/test_fake.py`: Tests refactored to use local data and unittest.TestCase

## Running Tests
```bash
cd case_after
PYTHONPATH=src pytest tests/
```

Expected: Tests pass without network access, can run in isolated VM.

## Testing Isolation
You can verify tests don't need network:
```bash
pytest -k 'not network' tests/  # No 'network' marker needed anymore
```
