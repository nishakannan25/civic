/// Phase 3 — Local Incident Data Source.
///
/// Interface and concrete implementation for persisting and querying
/// incident records and associated image files in local storage.

import 'dart:io';
import '../../../core/storage/local_database.dart';
import '../../../core/storage/local_image_storage.dart';
import '../models/local_incident.dart';

abstract class ILocalIncidentDataSource {
  Future<void> saveIncident(LocalIncident incident);
  Future<LocalIncident?> getIncident(String localId);
  Future<List<LocalIncident>> getAllIncidents();
  Future<List<LocalIncident>> getPendingIncidents();
  Future<List<LocalIncident>> getFailedIncidents();
  Future<void> updateSyncStatus(
    String localId,
    String status, {
    int? serverId,
    String? imageUrl,
    String? error,
    int? syncAttempts,
  });
  Future<void> deleteIncident(String localId);
  Future<String> copyImageToLocalStorage(String tempImagePath, String localIncidentId);
  Future<void> cleanupImage(String localImagePath);
}

class LocalIncidentDataSource implements ILocalIncidentDataSource {
  final LocalDatabase _database;
  final LocalImageStorage _imageStorage;

  LocalIncidentDataSource({
    LocalDatabase? database,
    LocalImageStorage? imageStorage,
  })  : _database = database ?? LocalDatabase(),
        _imageStorage = imageStorage ?? LocalImageStorage();

  @override
  Future<void> saveIncident(LocalIncident incident) async {
    await _database.insertIncident(incident);
  }

  @override
  Future<LocalIncident?> getIncident(String localId) async {
    return _database.getIncident(localId);
  }

  @override
  Future<List<LocalIncident>> getAllIncidents() async {
    return _database.getAllIncidents();
  }

  @override
  Future<List<LocalIncident>> getPendingIncidents() async {
    return _database.getPendingIncidents();
  }

  @override
  Future<List<LocalIncident>> getFailedIncidents() async {
    return _database.getFailedIncidents();
  }

  @override
  Future<void> updateSyncStatus(
    String localId,
    String status, {
    int? serverId,
    String? imageUrl,
    String? error,
    int? syncAttempts,
  }) async {
    await _database.updateSyncStatus(
      localId,
      status,
      serverId: serverId,
      imageUrl: imageUrl,
      error: error,
      syncAttempts: syncAttempts,
    );
  }

  @override
  Future<void> deleteIncident(String localId) async {
    final incident = await _database.getIncident(localId);
    if (incident != null) {
      await _imageStorage.deleteImage(incident.localImagePath);
      await _database.deleteIncident(localId);
    }
  }

  @override
  Future<String> copyImageToLocalStorage(String tempImagePath, String localIncidentId) async {
    return _imageStorage.saveImage(tempImagePath, localIncidentId);
  }

  @override
  Future<void> cleanupImage(String localImagePath) async {
    await _imageStorage.deleteImage(localImagePath);
  }
}
