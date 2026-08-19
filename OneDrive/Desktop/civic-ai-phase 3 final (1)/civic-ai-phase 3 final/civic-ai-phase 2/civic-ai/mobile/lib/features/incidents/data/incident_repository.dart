/// Phase 3 — Incident Repository.
///
/// Coordinates between LocalIncidentDataSource (device persistence) and
/// RemoteIncidentDataSource (FastAPI backend).
/// Implements offline-first incident creation, sync queues, and duplicate prevention.

import 'dart:io';
import '../../../core/connectivity/connectivity_service.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/network/api_client.dart';
import '../../../core/utils/logger.dart';
import '../models/incident_model.dart';
import '../models/local_incident.dart';
import '../models/location_data.dart';
import 'local_incident_data_source.dart';
import 'remote_incident_data_source.dart';

class IncidentRepository {
  final ILocalIncidentDataSource _localDataSource;
  final IRemoteIncidentDataSource _remoteDataSource;
  final IConnectivityService _connectivityService;

  IncidentRepository({
    ILocalIncidentDataSource? localDataSource,
    IRemoteIncidentDataSource? remoteDataSource,
    IConnectivityService? connectivityService,
    ApiClient? apiClient,
  })  : _localDataSource = localDataSource ?? LocalIncidentDataSource(),
        _remoteDataSource = remoteDataSource ?? RemoteIncidentDataSource(apiClient: apiClient ?? ApiClient()),
        _connectivityService = connectivityService ?? ConnectivityService();

  /// Legacy / Phase 2 compatibility method: submits an incident and returns IncidentModel.
  Future<IncidentModel> createIncident({
    required String imagePath,
    required int citizenRating,
    required LocationCaptureResult locationResult,
  }) async {
    final local = await submitIncident(
      imagePath: imagePath,
      citizenRating: citizenRating,
      locationResult: locationResult,
    );

    return IncidentModel(
      id: local.serverId ?? 0,
      referenceId: local.referenceId,
      userId: local.userId,
      imageUrl: local.imageUrl,
      latitude: local.latitude,
      longitude: local.longitude,
      gpsAccuracy: local.gpsAccuracy,
      locationStatus: local.locationStatus,
      timestamp: local.timestamp,
      citizenRating: local.citizenRating,
      status: local.status,
      createdAt: local.createdAt,
    );
  }

  /// Submit an incident with offline-first support.
  ///
  /// 1. Saves incident locally in persistent storage with PENDING_SYNC status and copied image.
  /// 2. Checks connectivity:
  ///    - If online: attempts immediate upload.
  ///      - If successful: marks UPLOADED, records server ID, safely cleans up local image copy.
  ///      - If upload fails: keeps PENDING_SYNC for background sync queue.
  ///    - If offline: keeps PENDING_SYNC for background sync queue.
  Future<LocalIncident> submitIncident({
    required String imagePath,
    required int citizenRating,
    required LocationCaptureResult locationResult,
  }) async {
    final now = DateTime.now().toUtc();
    final localId = 'loc-${now.millisecondsSinceEpoch}-${citizenRating}';

    // Step 1: Copy image to persistent application storage
    final persistentImagePath = await _localDataSource.copyImageToLocalStorage(imagePath, localId);

    // Step 2: Create local incident record with PENDING_SYNC status
    var localIncident = LocalIncident(
      localId: localId,
      localImagePath: persistentImagePath,
      latitude: locationResult.isAvailable && locationResult.location != null
          ? locationResult.location!.latitude
          : null,
      longitude: locationResult.isAvailable && locationResult.location != null
          ? locationResult.location!.longitude
          : null,
      gpsAccuracy: locationResult.isAvailable && locationResult.location != null
          ? locationResult.location!.accuracy
          : null,
      locationStatus: locationResult.status,
      timestamp: now,
      citizenRating: citizenRating,
      status: LocalIncidentStatus.pendingSync,
      createdAt: now,
      updatedAt: now,
    );

    await _localDataSource.saveIncident(localIncident);
    AppLogger.i('Incident saved locally: ${localIncident.localId} (Status: ${localIncident.status})');

    // Step 3: Check connectivity
    final isOnline = await _connectivityService.isConnected();
    if (!isOnline) {
      AppLogger.i('Device is offline. Incident ${localIncident.localId} queued for sync.');
      return localIncident;
    }

    // Step 4: Attempt immediate upload
    try {
      await _localDataSource.updateSyncStatus(localIncident.localId, LocalIncidentStatus.uploading);
      final response = await _remoteDataSource.uploadIncident(localIncident);

      final serverId = response['id'] as int;
      final serverImageUrl = response['image_url'] as String?;

      await _localDataSource.updateSyncStatus(
        localIncident.localId,
        LocalIncidentStatus.uploaded,
        serverId: serverId,
        imageUrl: serverImageUrl,
      );

      // Refresh local incident record
      localIncident = (await _localDataSource.getIncident(localIncident.localId)) ?? localIncident;
      AppLogger.i('Incident uploaded immediately: Server ID $serverId');

      // Safe cleanup of temporary camera file if different from persistent file
      if (imagePath != persistentImagePath) {
        try {
          final tempFile = File(imagePath);
          if (await tempFile.exists()) await tempFile.delete();
        } catch (_) {}
      }

      return localIncident;
    } catch (e) {
      AppLogger.w('Immediate upload failed for ${localIncident.localId}: $e. Keeping in PENDING_SYNC queue.');
      await _localDataSource.updateSyncStatus(
        localIncident.localId,
        LocalIncidentStatus.pendingSync,
        error: e.toString(),
      );
      localIncident = (await _localDataSource.getIncident(localIncident.localId)) ?? localIncident;
      return localIncident;
    }
  }

  /// Retrieve all pending incidents waiting to sync
  Future<List<LocalIncident>> getPendingIncidents() => _localDataSource.getPendingIncidents();

  /// Retrieve all failed incidents
  Future<List<LocalIncident>> getFailedIncidents() => _localDataSource.getFailedIncidents();

  /// Retrieve all local incident records
  Future<List<LocalIncident>> getAllLocalIncidents() => _localDataSource.getAllIncidents();

  /// Retrieve a single incident by local ID
  Future<LocalIncident?> getIncident(String localId) => _localDataSource.getIncident(localId);

  /// Mark incident as uploading
  Future<void> markUploading(String localId) =>
      _localDataSource.updateSyncStatus(localId, LocalIncidentStatus.uploading);

  /// Mark incident as successfully uploaded
  Future<void> markUploaded(String localId, int serverId, {String? imageUrl}) =>
      _localDataSource.updateSyncStatus(
        localId,
        LocalIncidentStatus.uploaded,
        serverId: serverId,
        imageUrl: imageUrl,
      );

  /// Mark incident as failed after retries exhausted
  Future<void> markFailed(String localId, String error, {int? syncAttempts}) =>
      _localDataSource.updateSyncStatus(
        localId,
        LocalIncidentStatus.failed,
        error: error,
        syncAttempts: syncAttempts,
      );

  /// Record a temporary sync failure and update retry attempt count on the SAME incident
  Future<void> recordSyncFailure(
    String localId,
    String error, {
    required int syncAttempts,
  }) =>
      _localDataSource.updateSyncStatus(
        localId,
        LocalIncidentStatus.pendingSync,
        error: error,
        syncAttempts: syncAttempts,
      );

  /// Reset a failed incident back to PENDING_SYNC for manual retry
  Future<void> retryIncident(String localId) async {
    final incident = await _localDataSource.getIncident(localId);
    if (incident != null) {
      final updated = incident.copyWith(
        status: LocalIncidentStatus.pendingSync,
        lastSyncError: null,
      );
      await _localDataSource.saveIncident(updated);
    }
  }

  /// Clean up local image after successful upload confirmation
  Future<void> deleteLocalImage(String imagePath) => _localDataSource.cleanupImage(imagePath);

  /// Delete a local incident record
  Future<void> deleteLocalIncident(String localId) => _localDataSource.deleteIncident(localId);
}
