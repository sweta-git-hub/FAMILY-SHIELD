// Family Voice Shield - Mobile Audio Streaming Client (Dart/Flutter)
// Mirrors server/client_replay.py for on-device mic PCM streaming

import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

class RiskScoreMessage {
  final double t;
  final double sA;
  final double sT;
  final double sC;
  final double risk;
  final String tier;
  final List<String> reasons;
  final String prompt;
  final bool mock;

  RiskScoreMessage({
    required this.t,
    required this.sA,
    required this.sT,
    required this.sC,
    required this.risk,
    required this.tier,
    required this.reasons,
    required this.prompt,
    required this.mock,
  });

  factory RiskScoreMessage.fromJson(Map<String, dynamic> json) {
    return RiskScoreMessage(
      t: (json['t'] as num?)?.toDouble() ?? 0.0,
      sA: (json['s_a'] as num?)?.toDouble() ?? 0.0,
      sT: (json['s_t'] as num?)?.toDouble() ?? 0.0,
      sC: (json['s_c'] as num?)?.toDouble() ?? 0.0,
      risk: (json['risk'] as num?)?.toDouble() ?? 0.0,
      tier: json['tier'] as String? ?? 'GREEN',
      reasons: (json['reasons'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      prompt: json['prompt'] as String? ?? 'normal',
      mock: json['mock'] as bool? ?? true,
    );
  }
}

abstract class WebSocketChannelAdapter {
  void sendBytes(Uint8List bytes);
  void sendText(String text);
  Stream<dynamic> get stream;
  Future<void> close([int? code, String? reason]);
}

class AudioStreamClient {
  final String baseUrl;
  final int sampleRate;
  final int channels;
  final int frameDurationMs;

  WebSocketChannelAdapter? _channel;
  StreamController<RiskScoreMessage>? _scoreController;
  bool _isConnected = false;

  AudioStreamClient({
    required this.baseUrl,
    this.sampleRate = 16000,
    this.channels = 1,
    this.frameDurationMs = 100,
  });

  bool get isConnected => _isConnected;
  Stream<RiskScoreMessage> get scoreStream =>
      _scoreController?.stream ?? const Stream.empty();

  void attachChannel(WebSocketChannelAdapter channel, String sessionId) {
    _channel = channel;
    _scoreController = StreamController<RiskScoreMessage>.broadcast();
    _isConnected = true;

    // Send handshake
    _channel!.sendText(jsonEncode({
      'type': 'start',
      'session': sessionId,
      'sr': sampleRate,
      'channels': channels,
      'lang': 'auto',
    }));

    _channel!.stream.listen((message) {
      if (message is String) {
        try {
          final data = jsonDecode(message) as Map<String, dynamic>;
          if (data['type'] == 'score') {
            _scoreController?.add(RiskScoreMessage.fromJson(data));
          }
        } catch (_) {}
      }
    }, onDone: () {
      _isConnected = false;
      _scoreController?.close();
    });
  }

  void sendCallContext({bool unknownNumber = true, bool claimsRelative = true}) {
    if (_isConnected && _channel != null) {
      _channel!.sendText(jsonEncode({
        'type': 'context',
        'unknown_number': unknownNumber,
        'claims_relative': claimsRelative,
      }));
    }
  }

  void sendAudioFrame(Uint8List pcmBytes) {
    if (_isConnected && _channel != null) {
      _channel!.sendBytes(pcmBytes);
    }
  }

  Future<void> disconnect() async {
    if (_isConnected && _channel != null) {
      _channel!.sendText(jsonEncode({'type': 'end'}));
      await _channel!.close(1000, 'Normal stream teardown');
      _isConnected = false;
      await _scoreController?.close();
    }
  }
}
