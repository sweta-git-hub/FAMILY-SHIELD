# 01 Architecture: Family Voice Shield

## 1. System Overview & Component Diagram

```
+-----------------------------------------------------------------------------------+
| CLIENT (Mobile App - Guardian / Member Roles)                                     |
|                                                                                   |
|  +--------------------+        +---------------------+        +-----------------+ |
|  | In-Person Pairing  | <----> | Secure Storage      | <----> | TOTP / Crypto   | |
|  | (QR Code Exchange) |        | (Keystore/Keychain) |        | Engine (Offline)| |
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
1. **Zero-Knowledge Architecture**: Master pairing secret $K_{pair} \in \{0,1\}^{160}$ generated via CSPRNG on the Guardian phone and scanned by Member via QR. The server never sees $K_{pair}$.
2. **Directional Keys (HKDF-SHA256)**:
   - $K_{A \to B} = \text{HKDF-SHA256}(K_{pair}, \text{info}=\text{"FVS1|A->B"}, L=20)$
   - $K_{B \to A} = \text{HKDF-SHA256}(K_{pair}, \text{info}=\text{"FVS1|B->A"}, L=20)$
   This prevents relay attacks where an attacker tricks a member into revealing their code and repeats it back to the parent.
3. **Rotating Code (RFC 6238 TOTP)**:
   - Time step $X = 30$ seconds, $T_0 = 0$.
   - $T = \lfloor \text{unix\_time} / 30 \rfloor$.
   - Formats:
     - 6-digit numeric ($\text{digits} = \text{bin} \pmod{10^6}$)
     - 2-word phonetic encoding ($w_1 = \text{bin} \pmod{2048}, w_2 = (\text{bin} \gg 11) \pmod{2048}$) using an indexed 2,048-word lexicon.
4. **Verification Window & Lockout State Machine**:
   - Verification accepts $T \in \{T_c - 1, T_c, T_c + 1\}$ to tolerate network/clock jitter.
   - Max 3 invalid attempts per challenge session before entering `LOCKED` state.
   - Fail closed: any error or lockout causes the app to recommend immediate hang-up and escalation to family alert.
5. **Duress Protocol**:
   - Distinct derived duress code (or intentional offset) allowing an assaulted user to present a code that appears accepted to the attacker while silently triggering emergency notifications.
