# 08 Data, Lexicon and Models

## 1. Word List for Phonetic Codes (2,048 Words)
- Based on standard 2048-word English dictionary (BIP-0039 standard wordlist).
- Index range: 0 to 2047 (11 bits per word).
- 2 words provide $2048 \times 2048 = 4,194,304$ combinations ($\approx 22$ bits of entropy).
- Words are phonetically distinct, simple to pronounce, and familiar to non-native English speakers.

## 2. Scam Lexicon (Reference for Phase 5)
Key signals and weights (1: weak, 2: medium, 3: high):
- **Urgency (Weight 2)**: "immediately", "right now", "turant", "jaldi", "abhi ke abhi".
- **Secrecy / Isolation (Weight 3)**: "don't tell anyone", "don't tell mom", "kisi ko mat batana", "phone mat kaatna".
- **Fear / Authority (Weight 3)**: "under arrest", "police case", "CBI", "digital arrest", "giraftaar".
- **Distress (Weight 2)**: "in trouble", "accident", "hospital mein", "bacha lo".
- **Payment Steering (Weight 3)**: "UPI karo", "GPay", "PhonePe", "scan QR", "approve request".
- **Device Excuse (Weight 2)**: "new number", "friend's phone", "phone kharab ho gaya".

## 3. Data Privacy & Ethics Commitments
- Zero raw audio or transcripts stored on server.
- Synthetic audio strictly generated with consent and prefixed `SYNTH_`.
