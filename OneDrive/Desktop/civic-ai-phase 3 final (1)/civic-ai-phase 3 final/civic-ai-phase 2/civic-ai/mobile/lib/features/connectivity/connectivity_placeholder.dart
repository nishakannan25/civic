/// Phase 3 — Backward-compatible export for connectivity service.
import '../../core/connectivity/connectivity_service.dart';

export '../../core/connectivity/connectivity_service.dart';

class ConnectivityPlaceholderService implements IConnectivityService {
  final ConnectivityService _service = ConnectivityService();

  @override
  Future<bool> isConnected() => _service.isConnected();

  @override
  Stream<bool> get onConnectivityChanged => _service.onConnectivityChanged;

  @override
  void dispose() => _service.dispose();
}
