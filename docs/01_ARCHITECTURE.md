# 01 Architecture: Family Voice Shield

## 1. System Overview & Component Diagram

```
+-----------------------------------------------------------------------------------+
| CLIENT (Mobile App - Guardian / Member Roles)                                     |
|                                                                                   |
|  +--------------------+        +---------------------+        +-----------------+ |
|  | In-Person Pairing  | <----> | Secure Storage      | <----> | TOTP / Crypto   | |
|  | (QR / Contact Exch)|        | (Keystore/Keychain) |        | Engine (Offline)| |
|  +--------------------+        +---------------------+        +-----------------+ |
|                                                                        |          |
|  +--------------------+        +---------------------+                 v          |
|  | Mic Capture        |        | Verify-Caller UI    | <------- [Code Matching]   |
|  | (Speakerphone/PCM) |        | (Voice Prompts /    |                            |
|  +--------------------+        |  Big Buttons)       |                            |
|           |                    +---------------------+                            |
|           | (16 kHz PCM)                  ^                                       |
+-----------|-------------------------------|---------------------------------------+
            | (WSS /v1/stream)              | (Scores, Tiers, Trigger Commands)
            v                               |
+-----------------------------------------------------------------------------------+
| SERVER (Stateless FastAPI Backend)        |                                       |
|                                           |                                       |
|  +-------------------------------------+  |                                       |
|  | Audio Ring Buffer & Chunker (3.0s)  |  |                                       |
|  +-------------------------------------+  |                                       |
|           |                               |                                       |
|     +-----+----------------+              |                                       |
|     v                      v              |                                       |
|  +--------------+    +------------------+ |                                       |
|  | STT Worker   |    | Anti-Spoof Model | |                                       |
|  | (Whisper)    |    | (AASIST/ONNX)    | |                                       |
|  +--------------+    +------------------+ |                                       |
|        |                   |              |                                       |
|        v                   |              |                                       |
|  +----------------+        |              |                                       |
|  | Scam Classifier|        |              |                                       |
|  | (Rules + LR)   |        |              |                                       |
|  +----------------+        |              |                                       |
|        |                   |              |                                       |
|        +----------+--------+              |                                       |
|                   v                       |                                       |
|         +-------------------+             |                                       |
|         | Fusion & Decision |-------------+                                       |
|         | Engine (Tiers)    |                                                     |
|         +-------------------+                                                     |
+-----------------------------------------------------------------------------------+
```

## 2. Core Security & Cryptographic Model
1. **Zero-Knowledge Architecture**: Master pairing secret $K_{pair} \in \{0,1\}^{160}$ generated via CSPRNG on the initiating phone and exchanged out-of-band via contact invite token or QR. The server never sees $K_{pair}$.
2. **Directional Keys (HKDF-SHA256)**:
   - $K_{A \to B} = \text{HKDF-SHA256}(K_{pair}, \text{info}=\text{"FVS1|A->B"}, L=20)$
   - $K_{B \to A} = \text{HKDF-SHA256}(K_{pair}, \text{info}=\text{"FVS1|B->A"}, L=20)$
   This prevents relay attacks where an attacker tricks a member into revealing their code and repeats it back to the parent.
3. **Rotating Code (RFC 6238 TOTP with 60-Second Window)**:
   - Time step $X = 60$ seconds, $T_0 = 0$ (per ADR-006).
   - $T = \lfloor \text{unix\_time} / 60 \rfloor$.
   - Pure 6-digit numeric ($\text{digits} = \text{bin} \pmod{10^6}$), providing 1-minute stress-free reading for seniors.
4. **Encrypted Local Vault**:
   - Relationships stored in local encrypted vault sealed with PBKDF2-HMAC-SHA256 and HMAC-SHA256 integrity tag. Zero secrets in cleartext logs.
5. **Verification Window & Lockout State Machine**:
   - Verification accepts $T \in \{T_c - 1, T_c, T_c + 1\}$ to tolerate network/clock jitter.
   - Max 3 invalid attempts per challenge session before entering `LOCKED` state.
   - Fail closed: any error or lockout causes the app to recommend immediate hang-up and escalation to family alert.
6. **Duress Protocol**:
   - Distinct derived duress code (or intentional offset) allowing an assaulted user to present a code that appears accepted to the attacker while silently triggering emergency notifications.

---

## 3. Real-Time Audio Streaming Pipeline (Phase 4)

### 3.1 Ephemeral Session Token Issuance
Clients never connect directly to WebSocket endpoints anonymously. Prior to call analysis:
1. Client requests token via `POST /v1/session`.
2. Server `SessionManager` generates a cryptographically secure random token (via `secrets.token_urlsafe(32)`), stores an ephemeral in-memory record with TTL (3600s), and returns the token.
3. Tokens are bound to a session ID and strictly held in RAM; zero database queries or persistent records.

### 3.2 Bidirectional WebSocket Audio Stream (`/v1/stream?token=<token>`)
1. **Authentication**: Connection validates query parameter token against active session registry. Invalid or expired tokens receive WebSocket close code `4001`.
2. **Handshake**: Client sends JSON `{"type": "start", ...}` and receives `{"type": "ready", ...}`.
3. **Paced Audio Ingestion**: Client streams continuous 16 kHz 16-bit linear PCM mono frames at 100ms intervals (3,200 bytes per frame).
4. **Circular In-Memory Ring Buffer (`AudioChunker`)**:
   - Accumulates incoming binary PCM bytes strictly in RAM (`bytearray`/`memoryview`).
   - Slices continuous audio into sliding 3.0-second analysis windows (96,000 bytes) with a 1.0-second stride (32,000 bytes).
   - Automatically evicts oldest bytes if buffer capacity exceeds 12.0 seconds, preventing memory leaks during network backpressure.
   - Conforms to **Rule 7**: Zero raw audio bytes are ever written to disk or permanent storage.
5. **VAD Hook (`SimpleEnergyVAD`)**:
   - Measures normalized RMS energy of each 3.0s window.
   - Marks chunks with `has_speech = False` when audio energy falls below threshold (0.015), preventing needless classifier evaluations on ambient silence.
6. **Real-Time Score Delivery**:
   - Completed chunks are processed by the scoring pipeline.
   - Contract-compliant JSON score frames (`type: score`, `risk`, `tier`, `prompt`, `mock`) are pushed back over the WebSocket connection within milliseconds of chunk completion.
7. **Clean Teardown**:
   - Client sends `{"type": "end"}` or disconnects; server cleanly closes socket, evicts in-memory audio buffers, and deregisters session.

---

## 4. Semantic Scam-Phrase Engine & Intent Classification (Phase 5)

### 4.1 In-Memory Speech-to-Text Pipeline (`ml/stt_engine.py`)
1. **Zero-Disk Ingestion**:
   - The STT pipeline wraps `faster-whisper` (CTranslate2 INT8 quantized models) and an in-memory `MockSTTEngine`.
   - Binary 16 kHz 16-bit linear PCM audio chunks are transcoded purely within memory buffers (`io.BytesIO`) into in-memory WAV frames.
   - Under no circumstances is audio or transcripts written to disk or logged, upholding strict Rule 7 privacy guarantees.
2. **Multilingual Support**:
   - Optimized for Indian family call context: supports Hindi (`hi`), English (`en`), and code-mixed Hinglish.

### 4.2 Multilingual Scam Lexicon & Category Taxonomy (`ml/scam_lexicon.py`)
Organizes social engineering indicators into 6 core threat categories:
- **`authority`** ($p = 0.85$): Police, CBI, ED, Court warrants, "Digital Arrest", "थाना", "गिरफ्तार".
- **`secrecy`** ($p = 0.80$): Isolation tactics: "don't tell anyone", "kisi ko mat batana", "phone mat kaatna", "line par raho".
- **`financial`** ($p = 0.75$): Payment steering: "UPI karo", "GPay", "PhonePe", "scan QR", "approve request", "खाते में डालो".
- **`distress`** ($p = 0.70$): False emergencies: "accident", "hospital", "kidnap", "bail money", "bacha lo".
- **`urgency`** ($p = 0.55$): Time coercion: "immediately", "right now", "turant", "jaldi", "abhi ke abhi".
- **`device_excuse`** ($p = 0.50$): Unfamiliar number justification: "new number", "friend's phone", "phone kharab ho gaya".

### 4.3 Probabilistic Noisy-OR Bayesian Intent Classifier (`ml/scam_classifier.py`)
1. Rather than naive boolean matching, active cues $X = \{x_1, \dots, x_k\}$ are combined via a causal Noisy-OR Bayesian formulation:
   $$P(\text{Scam} \mid X) = 1 - (1 - p_0) \prod_{i: x_i = 1} (1 - p_i)$$
   where $p_0 = 0.05$ represents baseline background false positive probability, and $p_i$ is the causal probability of category $i$.
2. **Monotonic Risk Escalation**:
   - Mild urgency alone: $s_t \approx 0.57$
   - Urgency + Secrecy: $s_t \approx 0.91$
   - Authority + Secrecy + Financial: $s_t \approx 0.99$ (Triggering immediate RED alert tier).
3. **StreamScorer Integration**:
   - Semantic scam score $s_t$ feeds directly into the real-time stream feedback, replacing Phase 4 mock placeholders and dynamically setting risk tier (`GREEN`, `AMBER`, `RED`) and prompt instructions (`normal` vs `ask_for_code`).

---

## 5. Acoustic Anti-Spoofing & Telephony Codec Pipeline (Phase 6)

### 5.1 Telephony Codec & Channel Degradation Simulator (`ml/telephony_codec.py`)
Carrier voice calls in India and globally operate over legacy 2G/3G narrowband cellular channels, VoLTE, or VoIP:
1. **Bandpass Filtering (300 Hz - 3400 Hz)**: Cascaded 2nd-order Butterworth filters attenuate low rumbles ($<300\text{ Hz}$) and high frequencies ($>3400\text{ Hz}$) characteristic of carrier telephony.
2. **Narrowband Resampling (8 kHz)**: Antialiasing 2:1 decimation from 16 kHz to 8 kHz and linear interpolation upsampling.
3. **ITU-T G.711 Companding ($\mu$-law / A-law)**:
   - Logarithmic 8-bit companding ($F(x) = \text{sgn}(x) \frac{\ln(1 + \mu |x|)}{\ln(1 + \mu)}$ with $\mu=255$) introduces quantization noise characteristic of PSTN/cellular circuits.
4. **Packet Jitter & Loss Simulation**: Simulates carrier network drops by zeroing discrete 10ms/20ms voice frames.
5. **Purpose**: Prevents anti-spoofing detectors from triggering false-positive deepfake warnings on legitimate phone calls compressed by carrier networks.

### 5.2 Acoustic Feature Extraction & Artifact Detection (`ml/antispoof_engine.py`)
1. **Feature Extraction (`AcousticFeatureExtractor`)**:
   - **Zero-Crossing Rate (ZCR) Variance**: Measures prosodic and phonetic transition dynamics between voiced vowels and unvoiced consonants. Natural speech exhibits high dynamic variance ($\sigma_{zcr}^2 \ge 0.005$), whereas synthetic/concatenated speech exhibits unnaturally flat ZCR distributions.
   - **Pitch Periodicity & Autocorrelation Stability**: Tracks harmonic consistency across $80\text{ Hz} - 400\text{ Hz}$. Hyper-periodic pitch lock ($>0.94$) triggers synthetic voice warnings.
   - **Crest Factor / Energy Dynamics**: Detects dynamic range compression typical of neural vocoders.
   - **Telephony Compensation**: Dampens acoustic spoof probabilities when carrier bandpass signatures are detected without abnormal robotic flatness.
2. **Inference Wrappers**:
   - **`ONNXAntiSpoofEngine`**: Optional inference session for AASIST / RawNet ONNX models.
   - **`AcousticArtifactDetector`**: Pure-Python zero-dependency detector executing deterministically in any environment.
   - **`MockAntiSpoofEngine`**: In-memory mock engine for deterministic CI verification.
3. **Multimodal Scoring (`server/scorer.py`)**:
   - `StreamScorer` evaluates incoming 16 kHz PCM chunks with both STT (Phase 5) and Acoustic Anti-Spoof (Phase 6).
   - If either $s_a \ge 0.70$ (synthetic voice clone detected) or $s_t \ge 0.70$ (critical scam language detected), fused risk elevates immediately to **RED** tier and commands `ask_for_code`.

---

## 6. Multimodal Logistic Fusion & Alert Tier Engine (Phase 7)

### 6.1 Calibrated Logistic Fusion Model (`ml/fusion.py`)
To prevent arbitrary heuristic weightings, risk signals from acoustic, semantic, and context modalities are combined via a calibrated Generalized Linear Model with logit transforms:
$$z = w_0 + w_a \cdot \text{logit}(s_a) + w_t \cdot \text{logit}(s_t) + w_c \cdot s_c$$
$$\text{risk} = \sigma(z) = \frac{1}{1 + e^{-z}}$$
where:
- $w_0 = -1.20$: Prior calibration bias favoring normal benign personal calls.
- $w_a = 1.25$: Acoustic synthetic weight (voice clone detection).
- $w_t = 1.35$: Semantic scam language weight (Noisy-OR intent extraction).
- $w_c = 1.50$: Contextual weight (unknown number + claimed relative).

#### Fail-Safe Critical Threat Overrides:
To preserve life-safety guarantees:
- If $s_a \ge 0.70$ (critical synthetic voice clone confirmed), the threat is never suppressed by benign conversational words.
- If $s_t \ge 0.70$ (critical digital arrest/kidnapping extortion), natural acoustic qualities cannot suppress the scam intent.
- $\text{risk} = \max(\text{risk}, s_a, s_t)$ whenever either crosses the $0.70$ threshold.

### 6.2 Alert Tier State Machine & Hysteresis Debouncing (`core/alert_tiers.py`)
To prevent UI flapping on borderline calls (e.g. risk fluctuating around 0.40):
1. **Asymmetric State Transitions**:
   - **Fast Escalation**: Instantaneous jump to AMBER ($\ge 0.40$) or RED ($\ge 0.70$) on the very first chunk exceeding threshold.
   - **Damped De-escalation**: Requires risk to drop below hysteresis threshold ($< 0.60$ for RED $\to$ AMBER, $< 0.32$ for AMBER $\to$ GREEN) for at least 2 consecutive chunks.
2. **Action Commands**:
   - `GREEN`: `"normal"`
   - `AMBER`: `"ask_for_code"`
   - `RED`: `"ask_for_code"` + Emergency Family SOS trigger
3. **Bilingual Spoken Guidance**: Localized Hindi and English voice prompts spoken via device TTS for low-vision seniors.
4. **HMAC-Signed Emergency Broadcast**: Generates cryptographically sealed `EmergencyNotification` payloads with masked phone numbers for family distribution.

---

## 7. Demo Path & Evaluation Scenarios (Phase 8)

### 7.1 Scripted Evaluation Scenario Catalog (`demo/scenarios.py`)
To enable deterministic, reproducible hackathon evaluations without unpredictable network dependencies, 5 end-to-end evaluation scenarios mirror prevalent fraud patterns and benign usage across India:

| Scenario ID | Name | Category | Expected Tier | Target Time-to-AMBER | Target Time-to-RED | Key Defense Tested |
|---|---|---|---|---|---|---|
| **S1** | Fake Accident – Urgent UPI Demand | Scam | `RED` | $\le 4.0\text{s}$ | $\le 6.0\text{s}$ | Escalation from vague relative claim $\to$ financial demand $\to$ secrecy/isolation |
| **S2** | Digital Arrest – CBI Impersonation | Scam | `RED` | $0.0\text{s}$ | $\le 2.0\text{s}$ | Instant critical authority override on "Digital Arrest" + Aadhaar coercion |
| **S3** | Benign Family – Weekend Chat | Benign | `GREEN` | None (Stable) | None | False-positive rejection on casual multi-chunk Hindi conversation |
| **S4** | Relay Attack Defense – Stale Nonce | Edge/Security | `REJECTED` | None (Blocked) | None | Replayed audio token intercepted from prior session fails cryptographic nonce verification |
| **S5** | Covert Duress Call – Silent Alarm | Edge/Safety | `GREEN` (Cover) | None | None | Victim utters secret duress keyword ("Raju"); screen stays normal, silent HMAC emergency alert dispatched |

### 7.2 Telephony Audio Replay Harness (`demo/telephony_replay.py`)
1. **Channel Degradation Pipeline**:
   - Audio is generated as 16-bit 8 kHz mono linear PCM.
   - Processed through `TelephonyCodecSimulator` (ITU-T G.711 $\mu$-law compression, 300–3400 Hz voice bandpass filter, and quantization noise).
2. **Stream Scoring & SLA Tracking**:
   - Each 2.0s window is evaluated through `StreamScorer` (`MockSTTEngine`, `MockAntiSpoofEngine`, `MultimodalFusionEngine`, and `AlertStateMachine`).
   - Tracks Time-to-AMBER and Time-to-RED against strict project latency SLAs ($\le 8\text{s}$).
   - Measures p50, p95, and max processing latencies ($< 5\text{ms}$ in-memory).
   - Generates formatted terminal reports or structured JSON metrics.

### 7.3 Dual-Phone Web Simulator Walkthrough (`demo/web_simulator.py`)
1. **Interactive Evaluation Bar**:
   - Provides live scenario dropdown selector (`S1` through `S5`).
   - "Run Entire Scenario" executes full streaming pass with animated progress.
   - "Step Next Chunk" advances window-by-window for step-by-step judge presentations.
2. **Live Telemetry & Event Log**:
   - Visualizes chunk transcripts, individual modality scores ($s_a, s_t, s_c$), calibrated fused risk, and processing latencies.
   - Dynamic alert badges and audible bilingual speech advisories reflect real-time threat level transitions.
