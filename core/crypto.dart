// Family Voice Shield (FVS) - Core Cryptographic Library (Dart)
// RFC 4226 (HOTP), RFC 6238 (TOTP), HKDF-SHA256, 2-word encoding, and Lockout Session.

import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:crypto/crypto.dart';

enum VerificationResult {
  success,
  duress,
  invalid,
  lockedOut,
}

/// HKDF-Extract using HMAC-SHA256 per RFC 5869
Uint8List hkdfExtract(Uint8List? salt, Uint8List ikm) {
  final effectiveSalt = (salt == null || salt.isEmpty) ? Uint8List(32) : salt;
  final hmac = Hmac(sha256, effectiveSalt);
  final prk = hmac.convert(ikm).bytes;
  return Uint8List.fromList(prk);
}

/// HKDF-Expand using HMAC-SHA256 per RFC 5869
Uint8List hkdfExpand(Uint8List prk, Uint8List info, int length) {
  const hashLen = 32;
  final n = (length / hashLen).ceil();
  final okm = <int>[];
  var t = <int>[];

  for (var i = 1; i <= n; i++) {
    final input = <int>[...t, ...info, i];
    final hmac = Hmac(sha256, prk);
    t = hmac.convert(input).bytes;
    okm.addAll(t);
  }
  return Uint8List.fromList(okm.sublist(0, length));
}

/// HKDF-SHA256 Extract-and-Expand
Uint8List hkdfSha256(Uint8List ikm, {Uint8List? salt, Uint8List? info, int length = 20}) {
  final prk = hkdfExtract(salt, ikm);
  return hkdfExpand(prk, info ?? Uint8List(0), length);
}

/// Derive directional keys: K_A_to_B and K_B_to_A
Map<String, Uint8List> deriveDirectionalKeys(Uint8List kPair) {
  final infoAtoB = Uint8List.fromList(utf8.encode('FVS1|A->B'));
  final infoBtoA = Uint8List.fromList(utf8.encode('FVS1|B->A'));
  return {
    'A_to_B': hkdfSha256(kPair, info: infoAtoB, length: 20),
    'B_to_A': hkdfSha256(kPair, info: infoBtoA, length: 20),
  };
}

/// Derive duress key from directional key
Uint8List deriveDuressKey(Uint8List kDir) {
  final infoDuress = Uint8List.fromList(utf8.encode('FVS1|DURESS'));
  return hkdfSha256(kDir, info: infoDuress, length: 20);
}

/// Computes dynamically truncated 31-bit integer per RFC 4226
int hotpBin(Uint8List key, int counter) {
  final bdata = ByteData(8);
  bdata.setUint64(0, counter, Endian.big);
  final counterBytes = bdata.buffer.asUint8List();

  final hmac = Hmac(sha1, key);
  final mac = hmac.convert(counterBytes).bytes;

  final offset = mac[19] & 0x0F;
  final binCode = ((mac[offset] & 0x7F) << 24) |
      ((mac[offset + 1] & 0xFF) << 16) |
      ((mac[offset + 2] & 0xFF) << 8) |
      (mac[offset + 3] & 0xFF);

  return binCode;
}

/// Computes RFC 4226 HOTP numeric string
String hotp(Uint8List key, int counter, {int digits = 6}) {
  final binCode = hotpBin(key, counter);
  final code = binCode % pow(10, digits).toInt();
  return code.toString().padLeft(digits, '0');
}

/// Computes counter for timestamp
int totpCounter(int timestamp, {int step = 30, int t0 = 0}) {
  return ((timestamp - t0) / step).floor();
}

/// Computes RFC 6238 TOTP numeric string
String totp(Uint8List key, int timestamp, {int step = 30, int t0 = 0, int digits = 6}) {
  final counter = totpCounter(timestamp, step: step, t0: t0);
  return hotp(key, counter, digits: digits);
}

/// Verify numeric code with time window
bool verifyNumeric(
  Uint8List key,
  String candidate,
  int timestamp, {
  int step = 30,
  int t0 = 0,
  int digits = 6,
  int window = 1,
}) {
  final cleaned = candidate.trim();
  if (cleaned.length != digits) return false;

  final center = totpCounter(timestamp, step: step, t0: t0);
  for (var delta = -window; delta <= window; delta++) {
    final expected = hotp(key, center + delta, digits: digits);
    if (expected == cleaned) return true;
  }
  return false;
}

/// Lockout challenge session state machine
class LockoutSession {
  final Uint8List keyDir;
  late final Uint8List keyDuress;
  final int maxAttempts;
  int failedAttempts = 0;
  bool isLocked = false;
  bool isVerified = false;

  LockoutSession(this.keyDir, {this.maxAttempts = 3}) {
    keyDuress = deriveDuressKey(keyDir);
  }

  VerificationResult checkNumeric(
    String candidate,
    int timestamp, {
    int step = 30,
    int t0 = 0,
    int digits = 6,
    int window = 1,
  }) {
    if (isLocked) return VerificationResult.lockedOut;

    // Check duress
    if (verifyNumeric(keyDuress, candidate, timestamp, step: step, t0: t0, digits: digits, window: window)) {
      isVerified = true;
      return VerificationResult.duress;
    }

    // Check primary directional key
    if (verifyNumeric(keyDir, candidate, timestamp, step: step, t0: t0, digits: digits, window: window)) {
      isVerified = true;
      return VerificationResult.success;
    }

    failedAttempts++;
    if (failedAttempts >= maxAttempts) {
      isLocked = true;
      return VerificationResult.lockedOut;
    }
    return VerificationResult.invalid;
  }

  void reset() {
    failedAttempts = 0;
    isLocked = false;
    isVerified = false;
  }
}
