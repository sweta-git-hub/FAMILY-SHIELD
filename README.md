# Family Voice Shield (FVS)

> **Prove who is calling. A clone can copy a voice, but it cannot copy a secret.**

Family Voice Shield protects families against AI voice-clone emergency scams. Instead of relying solely on acoustic detection (which suffers high false-positive rates on compressed 8 kHz phone calls), FVS pairs family devices offline to generate rotating cryptographic verification codes (TOTP/word pairs). An accompanying AI warning layer listens for scam phrases and voice synthesis markers, automatically prompting the parent to ask for the code when risk is detected.

---

## Key Features
- **Offline & Zero-Knowledge**: Pairing secrets never leave user devices and are never transmitted to any server.
- **Directional Keys (HKDF-SHA256)**: Child-to-parent verification keys differ from parent-to-child keys, preventing relay / man-in-the-middle attacks.
- **Dual Representation**: Supports standard 6-digit numeric codes and 2-word phonetic phrases from a 2,048-word dictionary (easy for seniors to hear and enunciate).
- **Closed-Loop AI Trigger**: Speech-to-text (Whisper) and acoustic anti-spoofing automatically prompt the identity challenge upon detecting scam language (urgency, secrecy, payment steering).
- **Fail-Closed Security**: Automatic lockout after 3 failed attempts, with covert duress support.

---

## Repository Structure
```
familyshield/
├── core/                  # Cryptographic engine (pure Python & Dart)
├── mobile/                # Flutter mobile application (Guardian & Member roles)
├── server/                # FastAPI backend for real-time audio analysis
├── ml/                    # Speech-to-text & acoustic anti-spoofing models
├── demo/                  # Replay scripts and synthetic evaluation scenarios
├── infra/                 # Deployment, Docker, and orchestration configurations
├── tests/                 # Unit, parity, and integration test suites
├── docs/                  # Project specifications, architecture, and phase logs
│   ├── 00_PROJECT_BRIEF.md
│   ├── 01_ARCHITECTURE.md
│   ├── 02_PHASE_PLAN.md
│   ├── 03_PROGRESS_LOG.md
│   ├── 04_DECISIONS.md
│   ├── 05_BACKLOG.md
│   ├── 06_RUNBOOK.md
│   ├── 07_API_CONTRACTS.md
│   └── 08_DATA_AND_MODELS.md
├── RULE.md                # Agent working guidelines and permission gates
├── HANDOFF.md             # Fast-resume state document
└── README.md
```

---

## Quick Start (Documentation & Phase 0)
1. Read [RULE.md](file:///c:/Users/DELL/Desktop/familyshield/RULE.md) for project standards and permission gates.
2. Read [HANDOFF.md](file:///c:/Users/DELL/Desktop/familyshield/HANDOFF.md) for the latest project state.
3. Check the status board in [docs/02_PHASE_PLAN.md](file:///c:/Users/DELL/Desktop/familyshield/docs/02_PHASE_PLAN.md).
