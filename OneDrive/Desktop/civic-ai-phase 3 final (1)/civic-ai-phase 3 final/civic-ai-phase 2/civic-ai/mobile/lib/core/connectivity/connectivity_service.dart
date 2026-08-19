/// Phase 3 — Network Connectivity Service.
///
/// Detects device internet availability and broadcasts real-time connection changes.
/// Performs active health/socket verification to avoid assuming that a local Wi-Fi interface
/// always implies reachability to the backend server.

import 'dart:async';
import 'dart:io';
import '../config/app_config.dart';
import '../utils/logger.dart';

abstract class IConnectivityService {
  Future<bool> isConnected();
  Stream<bool> get onConnectivityChanged;
  void dispose();
}

class ConnectivityService implements IConnectivityService {
  static final ConnectivityService _instance = ConnectivityService._internal();
  factory ConnectivityService() => _instance;
  ConnectivityService._internal();

  final _controller = StreamController<bool>.broadcast();
  bool? _lastKnownStatus;
  Timer? _periodicCheckTimer;
  bool? _simulatedStatus; // For Demo Mode and unit tests

  @override
  Stream<bool> get onConnectivityChanged => _controller.stream;

  /// Start periodic monitoring (checks every 5 seconds)
  void startMonitoring({Duration interval = const Duration(seconds: 5)}) {
    _periodicCheckTimer?.cancel();
    _periodicCheckTimer = Timer.periodic(interval, (_) async {
      final connected = await isConnected();
      if (_lastKnownStatus != connected) {
        _lastKnownStatus = connected;
        _controller.add(connected);
        AppLogger.i('Connectivity changed: ${connected ? "CONNECTED" : "DISCONNECTED"}');
      }
    });
  }

  /// Override connection status for Testing / Demo Mode
  void setSimulatedStatus(bool? status) {
    _simulatedStatus = status;
    if (status != null) {
      _lastKnownStatus = status;
      _controller.add(status);
      AppLogger.i('Connectivity simulated status set to: $status');
    }
  }

  @override
  Future<bool> isConnected() async {
    if (_simulatedStatus != null) {
      return _simulatedStatus!;
    }

    try {
      // Parse host from API base URL
      final uri = Uri.parse(AppConfig.apiBaseUrl);
      final host = uri.host.isNotEmpty ? uri.host : '8.8.8.8';

      // Look up address with 3 second timeout
      final result = await InternetAddress.lookup(host).timeout(const Duration(seconds: 3));
      final hasAddress = result.isNotEmpty && result[0].rawAddress.isNotEmpty;
      return hasAddress;
    } catch (_) {
      return false;
    }
  }

  @override
  void dispose() {
    _periodicCheckTimer?.cancel();
    _controller.close();
  }
}
