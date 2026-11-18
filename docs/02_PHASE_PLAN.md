# 02 Phase Plan & Status Board

## Status Board

| Phase | Name | Branch | Goal | Status | Built | Left off | Decisions |
|---|---|---|---|---|---|---|---|
| 0 | Bootstrap & Docs | `phase/00-bootstrap` | Monorepo scaffold, docs skeleton, lint setup | DONE | Repo layout, docs/00-08, RULE.md, HANDOFF.md, README.md, pyproject.toml | CI lint hooks | ADR-001, ADR-002, ADR-003, ADR-004, ADR-005 |
| 1 | Crypto Core | `phase/01-crypto-core` | TOTP, HKDF, words, lockout, duress in Python & Dart | DONE | core/crypto.py, core/crypto.dart, core/wordlist.py, tests/test_crypto.py | Cross-language runner | ADR-004, ADR-005 |
| 2 | Pairing & Storage | `phase/02-pairing` | Contact/phone pairing, secure vault, live 60s 6-digit sync | DONE | core/phone_util.py, core/pairing.py, core/storage.py, demo/web_simulator.py, tests/test_pairing.py, tests/test_storage.py | Ready for Phase 3 | ADR-006 |
| 3 | Verify-Caller UX | `phase/03-verify-flow` | Big buttons, Hindi/English TTS, practice call | DONE | core/elderly_ux.py, tests/test_elderly_ux.py, demo/web_simulator.py | Ready for Phase 4 | - |
| 4 | Backend Stream | `phase/04-backend-stream` | FastAPI, WebSocket audio stream, chunker | DONE | server/main.py, server/chunker.py, server/session.py, server/scorer.py, server/client_replay.py, mobile/audio_stream_client.dart, infra/Dockerfile, tests/test_backend_stream.py | Ready for Phase 5 | - |
| 5 | Scam Engine | `phase/05-scam-engine` | STT wrapper, lexicon, noisy-OR classifier | DONE | ml/scam_lexicon.py, ml/scam_classifier.py, ml/stt_engine.py, server/scorer.py, server/stream.py, tests/test_scam_engine.py | Ready for Phase 6 | - |
| 6 | Anti-Spoof | `phase/06-antispoof` | Telephony simulator, ONNX model inference | DONE | ml/telephony_codec.py, ml/antispoof_engine.py, server/scorer.py, tests/test_antispoof.py | Ready for Phase 7 | - |
| 7 | Fusion & Alerts | `phase/07-fusion-alerts` | Logistic fusion, alert tiers, client triggers | DONE | ml/fusion.py, core/alert_tiers.py, server/scorer.py, server/stream.py, demo/web_simulator.py, tests/test_fusion_alerts.py | Ready for Phase 8 | - |
| 8 | Realistic Demo | `phase/08-demo-path` | Telephony/replay demo path, scripted cases | DONE | demo/scenarios.py, demo/telephony_replay.py, demo/web_simulator.py, tests/test_demo_scenarios.py | Ready for Phase 9 | - |
| 9 | Eval & Hardening | `phase/09-eval-hardening` | Red-team tests, privacy audit, metrics report | TODO | - | - | - |
| 10 | Pitch & Release | `phase/10-release` | Slide deck, fallback video, README runbook | TODO | - | - | - |

---

## Phase Details

### Phase 0: Bootstrap and Documentation Scaffold
- **Branch**: `phase/00-bootstrap`
- **Time-box**: 1.5 h
- **In scope**: Repository layout, docs/00 to docs/08, RULE.md, HANDOFF.md, ADR-001/002/003.
- **Out of scope**: Application code, models, audio capture.
- **Acceptance criteria**:
  - Fresh workspace tells a new agent what to do in under 10 minutes via `HANDOFF.md`.
  - docs/00 to docs/08 exist with real technical specifications.

### Phase 1: Crypto Core (TOTP, HKDF, Words, Lockout, Duress)
- **Branch**: `phase/01-crypto-core`
- **Time-box**: 2.0 h
- **In scope**:
  - Pure HOTP (RFC 4226) and TOTP (RFC 6238) implementations.
  - HKDF-SHA256 directional key derivation (`FVS1|A->B` vs `FVS1|B->A`).
  - 6-digit numeric and 2-word phonetic representations (2,048-word BIP-39 lexicon).
  - Verification window (-1, 0, +1 time steps) to handle clock skew.
  - Fail-closed lockout state machine (3 failed attempts -> lockout).
  - Duress code derivation and detection.
  - Shared JSON test vector file (`tests/fixtures/crypto_test_vectors.json`).
  - Python implementation (`core/crypto.py`) + Dart implementation (`core/crypto.dart`).
  - 100% test coverage with automated unit tests.
- **Out of scope**: UI, persistent secure storage, network transport.
- **Acceptance criteria**:
  - 100% of RFC 4226 and RFC 6238 vectors pass.
  - Parity test produces identical codes across test vectors.
  - Lockout fails closed.

### Phase 2: Pairing & Secure Storage (Contact-Based Pairing & 60s 6-Digit Sync)
- **Branch**: `phase/02-pairing`
- **Time-box**: 2.5 h
- **In scope**:
  - Contact-based family member addition: Enter/pick phone number with E.164 normalization (`core/phone_util.py`).
  - Secure Zero-Knowledge Pairing Protocol: Out-of-band / peer token handshake deriving directional HKDF keys without server secret exposure (`core/pairing.py`).
  - Encrypted local secure vault: Multi-member key storage, tamper protection, and revocation (`core/storage.py`).
  - Synchronized 6-digit TOTP generator & remaining-time ticker (RFC 6238, 60s interval per user decision).
  - Dual-device interactive demo interface (web simulator showing Guardian and Member devices side-by-side with real-time 60s countdown and live verification).
  - Comprehensive unit test suite in `tests/test_pairing.py` and `tests/test_storage.py`.
- **Out of scope**:
  - Live acoustic deepfake analysis and Whisper STT (Phases 4-6).
  - Production carrier cellular SMS gateway (mock/local transport for demo).
- **Acceptance criteria**:
  - Entering a phone number successfully creates a verified family pairing.
  - Both paired devices compute identical synchronized 6-digit codes at every 60s step.
  - Directional keys prevent reverse-impersonation ($A \to B \neq B \to A$).
  - Storage vault fails closed on missing/corrupted keys.
  - 100% automated test pass rate.

### Phase 3: Verify-Caller Flow and Elderly Accessibility UX
- **Branch**: `phase/03-verify-flow`
- **Time-box**: 2.5 h
- **In scope**:
  - Elderly-friendly large tactile keypad with oversized 24px+ digit entry and haptic/visual feedback.
  - High-contrast accessibility theme (minimum 7:1 WCAG contrast ratio for low-vision seniors).
  - Bilingual spoken audio prompts in English and Hindi (TTS for prompt, verification, warning, lockout).
  - Safe emergency actions: "Hang Up & Call Back" (`tel:` link to known verified contact) and "Notify Family" emergency broadcast.
  - Practice Call Mode ("अभ्यास कॉल मोड"): zero-risk training simulator allowing seniors to practice without lockout anxiety.
  - Core UX logic module in `core/elderly_ux.py`.
  - Comprehensive unit test suite in `tests/test_elderly_ux.py`.
  - Interactive simulator enhancement in `demo/web_simulator.py`.
- **Out of scope**:
  - Live Whisper STT streaming and ML anti-spoofing (Phases 4-6).
- **Acceptance criteria**:
  - Challenge verification completes in under 15 seconds.
  - Bilingual voice prompts work in both English and Hindi.
  - Practice mode runs isolated from actual live lockout counters.
  - Emergency callback button dials the true saved number.
  - 100% automated test pass rate.

### Phase 4: Backend Skeleton and Audio Streaming
- **Branch**: `phase/04-backend-stream`
- **Time-box**: 2.5 h
- **Status**: DONE
- **Goal and Objectives**:
  - Phone microphone audio reaches the server as clean 3-second chunks and a dummy score returns.
  - Establish a low-latency, bidirectional WebSocket audio streaming pipeline connecting mobile clients to the backend processing service.
  - Implement transient, in-memory sliding window chunking with zero disk writes, upholding Rule 7 privacy guarantees.
- **In scope**:
  - FastAPI web server scaffold with environment configuration and health endpoint (`GET /v1/health`).
  - Transient session token negotiation endpoint (`POST /v1/session`).
  - WebSocket audio streaming endpoint (`/v1/stream?token=<session_token>`) supporting `start`, binary 16-bit linear PCM (16 kHz, mono), `context`, `end`, and score feedback per `docs/07_API_CONTRACTS.md`.
  - In-memory audio ring buffer and chunker with a 3.0-second sliding analysis window and Voice Activity Detection (VAD) hook.
  - Contract-compliant dummy ML decision scorer (`MOCK`) returning mock risk scores, tiers, and prompts.
  - Structured, privacy-preserving logging strictly omitting raw audio data, transcripts, or personal identifiers.
  - Containerization setup (`infra/Dockerfile` and `infra/docker-compose.yml`).
  - Python test replay client (`server/client_replay.py`) to stream WAV/PCM files for realistic latency and protocol testing.
  - Comprehensive unit and integration test suite covering chunking, ring buffer overflow, session negotiation, and WebSocket message handling.
- **Out of scope**:
  - Real machine learning models (Whisper STT in Phase 5, AASIST synthetic speech detection in Phase 6).
  - Push notifications via FCM (Phase 7).
  - Long-term storage or user authentication beyond ephemeral session tokens.
- **Planned Commits (8 commits)**:
  1. `feat(server): scaffold FastAPI app with health check and config loader`
  2. `feat(server): implement transient session token endpoint`
  3. `feat(server): implement PCM audio chunker with in-memory ring buffer`
  4. `feat(server): implement WebSocket stream endpoint with dummy mock scorer`
  5. `feat(infra): add Dockerfile and docker-compose for backend server`
  6. `feat(client): implement audio streaming client and replay test utility`
  7. `test(server): add comprehensive unit and integration tests for streaming and chunker`
  8. `docs(phase-4): update API contracts, runbook, architecture, and phase plan`
- **Acceptance criteria**:
  - Phone/test client streams 60 seconds of speech; server logs correct chunk count; zero audio bytes or transcripts are persisted to disk or server logs.
  - WebSocket client disconnect and reconnect works cleanly without server crash or state leak.
  - Round-trip latency (client PCM frame sent -> server chunk processed -> mock score received) is measured and documented.
  - 100% automated test pass rate for chunker, endpoints, and streaming protocol.
- **Risks & Dependencies**:
  - **Dependencies**: Relies on Phase 0 repository structure, `docs/07_API_CONTRACTS.md`, and `RULE.md` Section 7 privacy mandates.
  - **Host Python Environment**: Python 3.14 on host requires repair/reinstall or a functional Python interpreter in PATH.
  - **External Dependencies**: Requires `fastapi`, `uvicorn`, `websockets`, `python-dotenv` (requires Gate G4 approval before installation).
  - **PCM Frame Alignment**: Risk of malformed frames or byte alignment mismatch handled via strict byte-length validation in the chunker.
  - **Data Privacy**: Strictly in-memory `io.BytesIO`/memoryview buffers to ensure zero disk exposure.

### Phase 5: STT and Scam-Phrase Engine
- **Branch**: `phase/05-scam-engine`
- **Time-box**: 2.5 h
- **Status**: DONE
- **Goal and Objectives**:
  - Convert 3-second audio speech segments into Hindi, English, and Hinglish transcripts.
  - Detect high-risk social engineering scam tactics (urgency, isolation, legal/police threats, financial steering, device excuse).
  - Compute calibrated semantic scam score $s_t \in [0.0, 1.0]$ via probabilistic Noisy-OR classification over matched intent categories.
  - Connect semantic scorer directly to streaming WebSocket pipeline replacing mock semantic scores.
- **In scope**:
  - Bilingual/Hinglish scam lexicon and category taxonomy (`ml/scam_lexicon.py`) covering Hindi (Devanagari + Romanized Hinglish) and English.
  - Semantic scam intent classifier with Noisy-OR probabilistic fusion (`ml/scam_classifier.py`).
  - STT inference engine wrapper (`ml/stt_engine.py`) supporting faster-whisper/whisper with robust lightweight regex/mock fallback for resource-constrained test environments.
  - Stream scorer integration (`server/scorer.py`) replacing mock $s_t$ with real semantic classifier scores.
  - Unit and integration tests covering lexicon matching, noisy-OR math, STT wrapper, and end-to-end streaming scoring (`tests/test_scam_engine.py`).
  - Documentation updates across `docs/01_ARCHITECTURE.md`, `docs/03_PROGRESS_LOG.md`, `docs/07_API_CONTRACTS.md`, `docs/08_DATA_AND_MODELS.md`, and `HANDOFF.md`.
- **Out of scope**:
  - Acoustic anti-spoofing / synthetic voice detection (Phase 6 AASIST/ONNX).
  - Logistic multimodal fusion across acoustic and semantic (Phase 7).
  - FCM push notifications to family members (Phase 7).
- **Planned Commits (6 commits)**:
  1. `feat(ml): implement bilingual scam lexicon and category taxonomy`
  2. `feat(ml): implement probabilistic noisy-or scam intent classifier`
  3. `feat(ml): implement speech-to-text engine wrapper with graceful fallbacks`
  4. `feat(server): integrate semantic scam scoring into streaming server pipeline`
  5. `test(ml): add comprehensive test suite for lexicon, classifier, and STT`
  6. `docs(phase-5): update architecture, progress log, runbook, and handoff`
- **Acceptance criteria**:
  - Lexicon accurately tags all 6 core scam categories across English, Hindi, and Hinglish phrases.
  - Noisy-OR classifier outputs properly bounded and monotonic probabilities $[0.0, 1.0]$.
  - Zero scam indicators yield $s_t < 0.15$ (baseline safe speech).
  - Multiple compound scam indicators (e.g. digital arrest + urgency + UPI payment) yield $s_t \ge 0.70$ (RED tier).
  - Zero audio bytes or intermediate transcripts are persisted to disk (Rule 7).
  - 100% automated test pass rate across unit and integration tests.

### Phase 6: Acoustic Anti-Spoofing and Telephony Simulator
- **Branch**: `phase/06-antispoof`
- **Time-box**: 2.5 h
- **Status**: DONE
- **Goal and Objectives**:
  - Implement acoustic synthetic speech (deepfake / voice clone) detection generating calibrated score $s_a \in [0.0, 1.0]$.
  - Implement telephony degradation and codec simulator (G.711 mu-law/A-law, 8 kHz downsampling, bandpass 300-3400 Hz, packet jitter) to evaluate detector robustness on low-bitrate carrier voice calls.
  - Extract acoustic spectral and temporal features (ZCR, spectral flatness, energy dynamics, harmonic periodicity) without external dependencies.
  - Provide ONNX runtime inference model wrapper with graceful fallback to calibrated acoustic artifact detector.
  - Integrate acoustic scoring into the streaming server pipeline (`server/scorer.py`), actively updating $s_a$ in WebSocket score frames.
- **In scope**:
  - Telephony codec simulator (`ml/telephony_codec.py`): G.711 $\mu$-law/A-law companding, 8 kHz resampling, 300-3400 Hz bandpass filtering, packet loss simulation.
  - Acoustic feature extraction & anti-spoof inference (`ml/antispoof_engine.py`): Zero-Crossing Rate (ZCR) variance, spectral dynamics, high-frequency energy ratios, ONNX wrapper, and mock engine.
  - Stream scorer integration (`server/scorer.py`): Replacing mock $s_a$ with live acoustic anti-spoof evaluation.
  - Comprehensive unit and integration test suite (`tests/test_antispoof.py`).
  - Documentation updates across `docs/01_ARCHITECTURE.md`, `docs/02_PHASE_PLAN.md`, `docs/03_PROGRESS_LOG.md`, `docs/08_DATA_AND_MODELS.md`, and `HANDOFF.md`.
- **Out of scope**:
  - Multimodal logistic regression fusion calibration (Phase 7).
  - FCM push notifications to family members (Phase 7).
- **Planned Commits (6 commits)**:
  1. `feat(ml): implement telephony codec simulator and degradation filter`
  2. `feat(ml): implement acoustic feature extraction and artifact detector`
  3. `feat(ml): implement onnx anti-spoof model wrapper with mock fallback`
  4. `feat(server): wire acoustic anti-spoof scoring into streaming pipeline`
  5. `test(ml): add comprehensive test suite for telephony codec and anti-spoofing`
  6. `docs(phase-6): update architecture, progress log, data models, and handoff`
- **Acceptance criteria**:
  - Telephony codec simulator supports round-trip G.711 $\mu$-law/A-law compression and 8 kHz resampling.
  - Acoustic anti-spoof engine computes calibrated $s_a \in [0.0, 1.0]$.
  - Synthetic test tones and vocoder-like artifacts trigger elevated $s_a \ge 0.70$.
  - Natural speech with typical human dynamic variation produces low $s_a \le 0.25$.
  - Server streaming scorer outputs real $s_a$ alongside real $s_t$ without latency degradation.
  - Zero raw audio bytes are persisted to disk or permanent storage.
  - 100% automated test pass rate.

### Phase 7: Multimodal Fusion & Client Alerts
- **Branch**: `phase/07-fusion-alerts`
- **Time-box**: 2.5 h
- **Status**: DONE
- **Goal and Objectives**:
  - Formulate calibrated logistic / generalized linear multimodal fusion model combining acoustic spoof score $s_a$, semantic scam score $s_t$, and contextual metadata $s_c$.
  - Implement alert tier state machine with hysteresis debouncing (GREEN, AMBER, RED) to prevent rapid flickering on boundary conditions.
  - Implement client trigger engine generating real-time UI action commands (`normal`, `ask_for_code`, `emergency_broadcast`).
  - Implement emergency notification dispatch hook preparing signed family broadcast alerts.
  - Integrate multimodal fusion and alert engine into `server/scorer.py` and dual-device web simulator.
- **In scope**:
  - Multimodal logistic fusion engine (`ml/fusion.py`): calibrated sigmoid formulation with logit transforms and extreme threat overrides.
  - Alert tier state machine (`core/alert_tiers.py`): hysteresis smoothing, fast escalation (1 chunk to RED), damped de-escalation, emergency notification generation.
  - Streaming server integration (`server/scorer.py`): rich alert payload serialization with `type: "alert"`.
  - Web simulator update (`demo/web_simulator.py`): dynamic visual alert banner, auto-trigger TOTP challenge, Hindi/English TTS speech alerts.
  - Comprehensive unit and integration test suite (`tests/test_fusion_alerts.py`).
  - Documentation updates across `docs/01_ARCHITECTURE.md`, `docs/02_PHASE_PLAN.md`, `docs/03_PROGRESS_LOG.md`, `docs/07_API_CONTRACTS.md`, and `HANDOFF.md`.
- **Out of scope**:
  - Live carrier cellular network Twilio SIP gateway (Phase 8).
  - External paid FCM gateway tokens (mock/local transport for demo).
- **Planned Commits (6 commits)**:
  1. `feat(ml): implement calibrated multimodal logistic fusion engine`
  2. `feat(core): implement alert tier state machine with hysteresis debouncing`
  3. `feat(server): wire fusion engine and alert dispatch into streaming scorer`
  4. `feat(demo): update dual-phone simulator with dynamic alert banners and triggers`
  5. `test(core): add comprehensive test suite for fusion, alerts, and state transitions`
  6. `docs(phase-7): update architecture, api contracts, progress log, and handoff`
- **Acceptance criteria**:
  - Calibrated logistic fusion strictly outputs probability in $[0.0, 1.0]$.
  - Extreme conditions ($s_a \ge 0.70$ or $s_t \ge 0.70$) guarantee immediate RED tier override.
  - Alert tier state machine prevents flapping on borderline scores via hysteresis.
  - Dual-phone simulator dynamically reflects AMBER and RED alert states with audio/visual feedback.
  - 100% automated test pass rate across unit and integration tests.

### Phase 8: Realistic End-to-End Demo Path
- **Branch**: `phase/08-demo-path`
- **Time-box**: 2.5 h
- **Status**: DONE
- **Goal and Objectives**:
  - Construct 5 realistic, timed end-to-end evaluation scenarios mirroring real fraud tactics in India (Fake Accident, Digital Arrest, Benign Family, Replay Attack, Duress Alert).
  - Implement a telephony replay streaming test harness simulating degraded PSTN carrier audio through the pipeline.
  - Integrate an interactive walkthrough scenario selector into the dual-phone web simulator for live judging.
  - Measure and report end-to-end performance targets (Time-to-Amber < 8s, verification time < 15s).
- **In scope**:
  - Scenario catalog definition (`demo/scenarios.py`): 5 structured scenarios with multi-chunk transcripts, acoustic cues, context flags, and expected tier progressions.
  - Telephony replay runner (`demo/telephony_replay.py`): CLI streaming degraded G.711 carrier audio through `StreamScorer` with real-time latency and trigger metrics.
  - Web simulator walkthrough enhancements (`demo/web_simulator.py`): one-click scenario runner, live event log, automated code verification and emergency buttons.
  - Automated test suite (`tests/test_demo_scenarios.py`): deterministic assertion of scenario progression, timing limits, and directional key defense.
  - Documentation updates across `docs/01_ARCHITECTURE.md`, `docs/02_PHASE_PLAN.md`, `docs/03_PROGRESS_LOG.md`, `docs/06_RUNBOOK.md`, and `HANDOFF.md`.
- **Out of scope**:
  - Paid carrier Twilio trunking gateway (mock local telephony channel used).
- **Commits Completed (5 commits)**:
  1. `feat(demo): define realistic scripted scam and benign scenario catalog`
  2. `feat(demo): implement telephony audio replay test harness with metrics`
  3. `feat(demo): integrate interactive scenario walkthrough into web simulator`
  4. `test(demo): add comprehensive automated test suite for all demo scenarios`
  5. `docs(phase-8): update runbook, architecture, progress log, and handoff`
- **Acceptance criteria achieved**:
  - All 5 scripted scenarios execute cleanly and achieve expected tier progressions.
  - Time-to-Amber achieved within $\le 4.0$ seconds on scam scenarios (well within $\le 8$s SLA).
  - Directional key attack (Scenario 4) fails verification and rejects call instantly.
  - Duress escape (Scenario 5) triggers silent emergency family notification while maintaining screen safety.
  - 100% automated test pass rate (110/110 passing across repository).







