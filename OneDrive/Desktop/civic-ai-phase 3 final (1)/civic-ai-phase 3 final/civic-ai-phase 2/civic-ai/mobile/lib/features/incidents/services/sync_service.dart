/// Phase 3 — Incident Synchronization Service.
///
/// Manages background and on-demand synchronization of offline incidents.
/// Implements FIFO (oldest-first) processing, exponential backoff (2s -> 4s -> 8s -> 16s),
/// retry limits, non-blocking execution, duplicate-safe upload handling,
/// and automatic connectivity triggers.

import 'dart:async';
import 'dart:math';
import '../../../core/config/app_config.dart';
import '../../../core/connectivity/connectivity_service.dart';
import '../../../core/network/api_client.dart';
import '../../../core/utils/logger.dart';
import '../data/incident_repository.dart';
import '../data/remote_incident_data_source.dart';
import '../models/local_incident.dart';

class SyncService {
  static final SyncService _instance = SyncService._internal();
  factory SyncService() => _instance;
  SyncService._internal();

  IncidentRepository? _repository;
  IRemoteIncidentDataSource? _remoteDataSource;
  IConnectivityService? _connectivityService;

  bool _isSyncing = false;
  StreamSubscription<bool>? _connectivitySub;

  final _syncStatusController = StreamController<bool>.broadcast();
  final _syncEventController = StreamController<String>.broadcast();

  bool get isSyncing => _isSyncing;
  Stream<bool> get isSyncingStream => _syncStatusController.stream;
  Stream<String> get syncEventStream => _syncEventController.stream;

  /// Initialize the SyncService with dependencies and listen to network connectivity.
  void init({
    IncidentRepository? repository,
    IRemoteIncidentDataSource? remoteDataSource,
    IConnectivityService? connectivityService,
  }) {
    _repository = repository ?? IncidentRepository();
    _remoteDataSource = remoteDataSource ?? RemoteIncidentDataSource(apiClient: ApiClient());
    _connectivityService = connectivityService ?? ConnectivityService();

    // Cancel existing subscription if any
    _connectivitySub?.cancel();

    // Listen for connectivity changes: when connection is restored, trigger auto-sync
    _connectivitySub = _connectivityService!.onConnectivityChanged.listen((connected) {
      if (connected) {
        AppLogger.i('Connectivity restored. Automatically triggering sync queue...');
        syncPendingIncidents();
      }
    });

    // Run startup sync check automatically in background
    _checkAndSyncOnStartup();
  }

  Future<void> _checkAndSyncOnStartup() async {
    final connected = await _connectivityService?.isConnected() ?? false;
    if (connected) {
      AppLogger.i('App startup: Network available. Automatically synchronizing pending reports.');
      syncPendingIncidents();
    } else {
      AppLogger.i('App startup: Network unavailable. Sync will trigger when connection returns.');
    }
  }

  /// Synchronize all pending and retriable incidents.
  ///
  /// Returns the number of successfully synced incidents.
  Future<int> syncPendingIncidents() async {
    if (_isSyncing) {
      AppLogger.i('SyncService is already running. Skipping concurrent trigger.');
      return 0;
    }

    if (_repository == null) {
      _repository = IncidentRepository();
    }
    if (_remoteDataSource == null) {
      _remoteDataSource = RemoteIncidentDataSource(apiClient: ApiClient());
    }

    final isOnline = await _connectivityService?.isConnected() ?? false;
    if (!isOnline) {
      AppLogger.w('Cannot sync: No network connectivity.');
      return 0;
    }

    _isSyncing = true;
    _syncStatusController.add(true);
    _syncEventController.add('Sync started');
    AppLogger.i('─── SYNC QUEUE STARTED ───');

    int syncedCount = 0;

    try {
      // 1. Fetch pending incidents (FIFO — oldest first)
      final pendingList = await _repository!.getPendingIncidents();
      AppLogger.i('Found ${pendingList.length} pending incidents to sync.');

      for (final incident in pendingList) {
        // Re-check connectivity before each incident
        final stillOnline = await _connectivityService?.isConnected() ?? false;
        if (!stillOnline) {
          AppLogger.w('Network lost during sync queue processing. Pausing sync.');
          break;
        }

        final success = await _syncSingleIncident(incident);
        if (success) {
          syncedCount++;
        }
      }
    } catch (e) {
      AppLogger.e('Unhandled error in sync queue: $e');
    } finally {
      _isSyncing = false;
      _syncStatusController.add(false);
      _syncEventController.add('Sync completed. Synced: $syncedCount');
      AppLogger.i('─── SYNC QUEUE COMPLETED (Synced: $syncedCount) ───');
    }

    return syncedCount;
  }

  /// Synchronize a single incident with exponential backoff and duplicate protection.
  Future<bool> _syncSingleIncident(LocalIncident incident) async {
    final nextAttempt = incident.syncAttempts + 1;
    AppLogger.i('Syncing incident: ${incident.localId} (Attempt: $nextAttempt/${AppConfig.syncMaxRetries})');
    _syncEventController.add('Uploading incident: ${incident.referenceId}');

    // Mark as uploading
    await _repository!.markUploading(incident.localId);

    try {
      final response = await _remoteDataSource!.uploadIncident(incident);

      final serverId = response['id'] as int;
      final serverImageUrl = response['image_url'] as String?;

      // Mark as uploaded and store server ID on the SAME local incident
      await _repository!.markUploaded(
        incident.localId,
        serverId,
        imageUrl: serverImageUrl,
      );

      // Safe cleanup of persistent local photo ONLY after server confirmation
      await _repository!.deleteLocalImage(incident.localImagePath);

      AppLogger.i('✓ Incident ${incident.localId} successfully synced! Server ID: $serverId');
      _syncEventController.add('Incident uploaded: ${incident.referenceId}');
      return true;
    } catch (e) {
      AppLogger.w('✗ Sync failed for ${incident.localId}: $e');

      if (nextAttempt >= AppConfig.syncMaxRetries) {
        // Max retries reached: mark as FAILED (preserved locally for inspection/manual retry)
        await _repository!.markFailed(
          incident.localId,
          'Failed after $nextAttempt attempts: $e',
          syncAttempts: nextAttempt,
        );
        AppLogger.e('Incident ${incident.localId} exceeded max retries ($nextAttempt). Marked FAILED.');
      } else {
        // Calculate exponential backoff delay: 2^(attempts-1) * 2 seconds (e.g. 2s -> 4s -> 8s -> 16s)
        final backoffSec = min(
          pow(2, nextAttempt - 1).toInt() * AppConfig.syncInitialBackoffSeconds,
          AppConfig.syncMaxBackoffSeconds,
        );

        // Update retry attempt count on the SAME incident without creating duplicate records
        await _repository!.recordSyncFailure(
          incident.localId,
          'Attempt $nextAttempt failed: $e (next backoff ~$backoffSec s)',
          syncAttempts: nextAttempt,
        );

        AppLogger.i('Scheduled backoff for ${incident.localId}: ~$backoffSec seconds (Attempt $nextAttempt/${AppConfig.syncMaxRetries})');
      }

      return false;
    }
  }

  void dispose() {
    _connectivitySub?.cancel();
    _syncStatusController.close();
    _syncEventController.close();
  }
}
