# 00 Project Brief: Family Voice Shield

## 1. Problem Statement
Voice-clone fraud impersonates children, grandchildren, or relatives in acute distress (fake accidents, arrests, hospital bills, virtual kidnapping). 
Scammers need only 3-5 seconds of harvested audio (from social media, reels, voicemails) to generate a convincing clone.
In India and globally, victims (predominantly parents and seniors aged 55+) lose funds within minutes via non-reversible UPI or bank transfers.

Existing advice ("agree on a family safe word") fails under extreme panic because:
1. Terrified parents forget to ask.
2. Static safe words are easily forgotten, overheard, or shared.
3. Callers without access to the app cannot recall long passphrases.
4. Voice detectors alone suffer high false-positive rates on compressed telephony (8 kHz) audio.

## 2. Solution Overview
Family Voice Shield (FVS) flips the paradigm: **Prove who is calling instead of guessing whether the voice is fake.**
- **Identity Layer (Layer 1)**: An offline, zero-knowledge rotating code (TOTP/HOTP) shared between family members via an in-person QR handshake. 
  - Uses 6 digits or 2 spoken words from a 2,048-word lexicon.
  - Derives separate directional keys for Caller->Receiver vs Receiver->Caller via HKDF-SHA256.
  - Enforces strict 3-attempt lockout and duress alerting.
- **AI Warning Layer (Layer 2)**: Listens during the call (via speakerphone mic or cloud stream) to detect scam language patterns (urgency, secrecy, payment steering, authority) and acoustic synthetic speech artifacts.
- **The Closed-Loop Trigger**: When AI risk crosses the Amber/Red threshold, the app **automatically commands the guardian** to ask for the code ("Ask for the family code"). The terrified parent never has to remember.

## 3. Users & Personas
- **Guardian (Parent/Senior)**: Receives calls. Needs large buttons, high contrast, spoken Hindi/English voice prompts, and zero technical friction.
- **Member (Adult Child/Relative)**: Voice potentially cloned. Initiates pairing, opens app to read the 30-second rotating code when asked.

## 4. Non-Goals (MVP)
- No in-line call interception on unrooted standard iOS/Android (uses speakerphone mic capture or cloud Twilio gateway for demo).
- No server-side storage of family secrets, raw audio, or conversation transcripts.
- No direct automated execution of financial transactions or UPI holds (mock family approval roadmap).

## 5. Success Criteria & Acceptance Targets
- Cryptographic identity core passes 100% of RFC 4226 & RFC 6238 test vectors.
- Verifications complete in under 15 seconds.
- Amber trigger fires within 8 seconds of scam speech onset.
- Zero audio, transcript, or private key data persisted on disk or server.
