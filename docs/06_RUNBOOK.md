# 06 Runbook

## Environment Requirements
- Python 3.10+
- (Later phases) Flutter 3.x / Dart 3.x

## Crypto Core Verification (Phase 1)
Run the test suite with standard Python unittest:
```bash
python -m unittest discover tests
```

Expected output:
```
Ran 9 tests in ~0.08s
OK
```

All 9 test suites verify:
1. RFC 4226 HOTP compliance (counter 0 through 9).
2. RFC 6238 TOTP compliance (SHA-1, 6-digit and 8-digit modes).
3. HKDF-SHA256 directional derivation ($K_{A \to B} \neq K_{B \to A}$).
4. Duress key derivation ($K_{duress} \neq K_{dir}$).
5. 2,048-word BIP-39 phonetic encoding and 22-bit round-trip.
6. Verification window handling ($\Delta t \in \{-1, 0, +1\}$).
7. Fail-closed lockout state machine (3 invalid attempts lock out session).
8. Covert duress detection without locking.
9. 1,000 deterministic parity vectors across random keys and timestamps.

## Resetting State
The crypto core is purely functional and stateless. No reset commands are necessary for Phase 1.
