# 03 Progress Log

### init | chore: initialize documentation scaffold and phase 0 | phase/00-bootstrap
- **Built**: Created `RULE.md`, `HANDOFF.md`, and `docs/00` through `docs/08`.
- **Why**: Establish rigorous agent rules, phase boundaries, security commitments, and architectural records.
- **Decision**: ADR-001 (Monorepo architecture with decoupled crypto core), ADR-002 (Identity before detection), ADR-003 (Platform call audio fallback).
- **Tests**: Documentation structure validated against report requirements.
- **Next**: Finalize Phase 0 files and repo structure.

### p0-done | chore: complete phase 0 scaffold, tooling, and readme | phase/00-bootstrap
- **Built**: Monorepo directory structure (`core/`, `mobile/`, `server/`, `ml/`, `demo/`, `infra/`, `tests/`), `README.md`, `.gitignore`, `.env.example`, and `pyproject.toml`.
- **Why**: Satisfy Phase 0 acceptance criteria per report Section 14.
- **Decision**: ADR-004 (6 digits and 2-word phonetic lexicon), ADR-005 (HKDF-SHA256 directional key derivation).
- **Tests**: Directory tree verified; all Phase 0 files verified.
- **Left off / next**: Phase 0 complete. Awaiting user Gate G1 permission to start Phase 1.

### p1-core | feat: implement pure-function crypto core, wordlist, and tests | phase/01-crypto-core
- **Built**: `core/crypto.py`, `core/crypto.dart`, `core/wordlist.py`, `tests/fixtures/crypto_test_vectors.json`, and `tests/test_crypto.py`.
- **Why**: Provide the offline zero-knowledge cryptographic identity layer (HOTP RFC 4226, TOTP RFC 6238, HKDF directional keys, 2048-word phonetic encoding, lockout state machine, and duress detection).
- **Decision**: ADR-004, ADR-005.
- **Tests**: 9 test suites covering RFC 4226 vectors, RFC 6238 vectors, HKDF directional keys, duress keys, 2-word phonetic encoding/decoding, clock-skew verification windows, 3-strike fail-closed lockout, and 1,000 deterministic parity vectors (`python -m unittest discover tests`). Result: 9/9 passed in 0.077s.
- **Left off / next**: Phase 1 complete. Awaiting user Gate G1 permission to start Phase 2 (Pairing & Secure Storage).
