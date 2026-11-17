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
