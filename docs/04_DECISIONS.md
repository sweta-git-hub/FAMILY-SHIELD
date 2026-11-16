# 04 Architecture Decision Records (ADR)

### ADR-001: Monorepo Architecture with Decoupled Pure-Function Crypto Core
- **Status**: Accepted
- **Date**: 2026-11-17
- **Context**: Family Voice Shield requires cryptographic code verification on both client (Flutter/Dart) and server/testing environments (Python).
- **Options Considered**:
  - A: Keep crypto logic embedded inside UI widgets.
  - B: Decoupled pure-function core implemented in Python and Dart sharing identical test vectors.
- **Decision**: Option B. Implement pure functions with no side effects, zero platform dependencies, and zero IO.
- **Consequences**: Easy unit testing, zero network reliance, and cross-platform verification.

### ADR-002: Identity Layer as Primary Protection; AI as Closed-Loop Trigger
- **Status**: Accepted
- **Date**: 2026-11-17
- **Context**: Phone call audio is compressed (8 kHz telephony) and synthetic voice detectors suffer from false positives and domain shift.
- **Options Considered**:
  - A: Rely on acoustic AI detector to label call as "fake" or "real".
  - B: Treat acoustic and semantic AI solely as risk detectors to trigger an offline zero-knowledge cryptographic identity challenge.
- **Decision**: Option B. "A clone can copy a voice, but it cannot copy a secret."
- **Consequences**: Protection remains absolute even if AI model encounters novel synthesis generators.

### ADR-003: Platform Call Audio Fallback Strategy
- **Status**: Accepted
- **Date**: 2026-11-17
- **Context**: Standard iOS and Android APIs restrict third-party apps from recording phone calls in background.
- **Options Considered**:
  - A: Claim background interception works on all devices (fails on judge inspection).
  - B: Explicit 2-path model: Speakerphone mic capture for hackathon demo; Twilio Media Stream for telephony evaluations; dialer role/carrier integration for long-term roadmap.
- **Decision**: Option B. Clear engineering honesty wins credibility.

### ADR-004: Code Format: 6 Digits and 2-Word Phonetic Lexicon
- **Status**: Accepted
- **Date**: 2026-11-17
- **Context**: A 4-digit code offers only ~13.3 bits of entropy (0.09% lucky guess chance in 3 tries) and is difficult for elderly users to enunciate in panic.
- **Options Considered**:
  - A: 4-digit numeric code.
  - B: 6-digit numeric code (19.9 bits) or 2-word code from 2,048-word lexicon (22 bits).
- **Decision**: Option B. Support both 6 digits and 2-word phonetic representations.

### ADR-005: Directional Key Derivation with HKDF-SHA256
- **Status**: Accepted
- **Date**: 2026-11-17
- **Context**: If both sides use the same key, an attacker can launch a relay attack (call member, get their code, and recite it to guardian).
- **Options Considered**:
  - A: Symmetric single key for both directions.
  - B: Derive distinct directional keys: $K_{A \to B}$ with info `"FVS1|A->B"` and $K_{B \to A}$ with info `"FVS1|B->A"`.
- **Decision**: Option B using HKDF-SHA256. Code shown on member's device can only verify them to the guardian, not vice-versa.
