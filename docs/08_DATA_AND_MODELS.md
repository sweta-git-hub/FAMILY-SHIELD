# 08 Data, Lexicon and Models

## 1. Word List for Phonetic Codes (2,048 Words)
- Based on standard 2048-word English dictionary (BIP-0039 standard wordlist).
- Index range: 0 to 2047 (11 bits per word).
- 2 words provide $2048 \times 2048 = 4,194,304$ combinations ($\approx 22$ bits of entropy).
- Words are phonetically distinct, simple to pronounce, and familiar to non-native English speakers.

## 2. Scam Lexicon and Category Taxonomy (Phase 5 Built)
The scam lexicon (`ml/scam_lexicon.py`) and Bayesian Noisy-OR classifier (`ml/scam_classifier.py`) formalize 6 core social engineering tactic categories across English, Hindi (Devanagari), and Hinglish:

| Category | Prior $p_i$ | Weight | Key Triggers (English / Hindi / Hinglish) | Description |
|---|---|---|---|---|
| `authority` | 0.85 | 3 (High) | "digital arrest", "police case", "CBI", "ED", "warrant", "डिजिटल अरेस्ट", "गिरफ्तार", "थाना" | Coercion via law enforcement, judicial threats |
| `secrecy` | 0.80 | 3 (High) | "don't tell anyone", "kisi ko mat batana", "phone mat kaatna", "लाइन पर रहो", "line par raho" | Isolation of senior victim from family support network |
| `financial` | 0.75 | 3 (High) | "UPI", "GPay", "PhonePe", "scan QR", "approve request", "पैसे भेजो", "खाते में डालो" | Demands for immediate digital fund transfer |
| `distress` | 0.70 | 2 (Medium) | "accident", "hospital", "ICU", "kidnap", "bail", "बचा लो", "खतरे में", "मदद करो" | False claims of physical injury or captivity |
| `urgency` | 0.55 | 2 (Medium) | "immediately", "right now", "turant", "jaldi", "abhi ke abhi", "तुरंत", "फटाफट" | Artificial time pressure to disable critical thinking |
| `device_excuse` | 0.50 | 2 (Medium) | "new number", "friend's phone", "phone kharab ho gaya", "दोस्त का फोन", "नया नंबर" | Fabricated justification for unknown caller ID |

### 2.1 Causal Noisy-OR Bayesian Formulation
The semantic scam score $s_t \in [0.0, 1.0]$ is computed as:
$$P(\text{Scam} \mid X) = 1 - (1 - p_0) \prod_{i \in \text{Active Categories}} (1 - p_i)$$
where:
- $p_0 = 0.05$ (background false positive leak rate for benign conversation).
- $p_i$ is the causal prior probability assigned to category $i$.

### 2.2 STT Engine Specifications
- **Model**: `faster-whisper` (`tiny`/`base` with INT8 quantization via CTranslate2).
- **Execution**: Purely transient in-memory PCM-to-WAV transcoding via `io.BytesIO`.
- **Target Languages**: Hindi (`hi`), English (`en`), and code-mixed Hinglish.
- **Rule 7 Compliance**: Zero audio or text persistence on disk.

## 3. Data Privacy & Ethics Commitments
- Zero raw audio or transcripts stored on server.
- Synthetic audio strictly generated with consent and prefixed `SYNTH_`.
