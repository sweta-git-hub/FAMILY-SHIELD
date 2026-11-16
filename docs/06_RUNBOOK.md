# 06 Runbook

## Environment Requirements
- Python 3.10+
- (Later phases) Flutter 3.x / Dart 3.x

## Crypto Core Verification (Phase 1)
Run the test suite with standard Python unittest:
```bash
python -m unittest discover tests
```

To run individual test modules:
```bash
python -m unittest tests.test_crypto
```

## Resetting State
The crypto core is purely functional and stateless. No reset commands are necessary for Phase 1.
