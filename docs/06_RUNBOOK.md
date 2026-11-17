# 06 Runbook

## Environment Requirements
- Python 3.10+
- (Later phases) Flutter 3.x / Dart 3.x

## Automated Test Suite (Phases 1, 2 & 3)
Run all 31 unit and parity tests:
```bash
python -m unittest discover tests
```

Expected output:
```
Ran 31 tests in ~0.13s
OK
```

All 31 test suites verify:
1. RFC 4226 HOTP compliance (counter 0 through 9).
2. RFC 6238 TOTP compliance (SHA-1, 6-digit and 8-digit modes).
3. HKDF-SHA256 directional derivation ($K_{A \to B} \neq K_{B \to A}$).
4. Duress key derivation ($K_{duress} \neq K_{dir}$).
5. 2,048-word BIP-39 phonetic encoding and 22-bit round-trip.
6. Verification window handling ($\Delta t \in \{-1, 0, +1\}$).
7. Fail-closed lockout state machine (3 invalid attempts lock out session).
8. Covert duress detection without locking.
9. 1,000 deterministic parity vectors across random keys and timestamps.
10. E.164 phone number normalization (domestic, international, invalid cases).
11. Contact profile creation and validation.
12. Zero-knowledge pairing invitation creation and acceptance.
13. Acceptance mismatch rejection (wrong recipient phone fails).
14. Synchronized 60-second 6-digit TOTP code agreement between Guardian and Member.
15. Directional isolation security (Rahul's code to Mom != Mom's code to Rahul).
16. 3-strike fail-closed lockout during incoming code verification.
17. Local vault storage, retrieval, peer-phone lookup, and revocation.
18. PBKDF2/HMAC encrypted vault export and import.
19. Tamper detection failure (tampered vault fails closed).
20. Bilingual voice prompt catalog completeness in English and Hindi.
21. Spoken prompt language switching.
22. High-contrast accessibility toggle state.
23. Emergency callback action URI generation (`tel:` link).
24. Family SOS emergency broadcast mock structure.
25. Practice call session evaluation and isolation from live lockout state.

## Interactive Dual-Device Web Simulator (Phases 2 & 3 Demo)
Launch the side-by-side interactive simulator in your browser:
```bash
python demo/web_simulator.py 8080
```
Open `http://localhost:8080/` in any browser:
- **Left phone**: Guardian (Mom).
- **Right phone**: Member (Rahul).
- **Language**: Toggle between English and हिंदी to hear and see spoken prompts.
- **Keypad**: Tap digits 0-9 on the large tactile keypad.
- **Emergency Action**: Test "Hang Up & Call Back" to break virtual kidnapping.
- **Practice Mode**: Click "Practice Call Mode" for an isolated training simulation.

## Resetting State
Vault records and sessions can be reset via the simulator UI ("Reset Strikes") or by re-instantiating fresh in-memory `SecureVault` instances.
