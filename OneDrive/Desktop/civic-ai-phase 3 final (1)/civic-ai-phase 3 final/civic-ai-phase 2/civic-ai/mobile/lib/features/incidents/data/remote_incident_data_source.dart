/// Phase 3 — Remote Incident Data Source.
///
/// Handles network communication with the FastAPI backend for incident uploads.
/// Attaches client idempotency keys to ensure duplicate submissions are recognized
/// and handled safely at the server level.

import 'dart:io';
import '../../../core/network/api_client.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/errors/exceptions.dart';
import '../models/local_incident.dart';

abstract class IRemoteIncidentDataSource {
  Future<Map<String, dynamic>> uploadIncident(LocalIncident incident);
}

class RemoteIncidentDataSource implements IRemoteIncidentDataSource {
  final ApiClient _apiClient;

  RemoteIncidentDataSource({required ApiClient apiClient}) : _apiClient = apiClient;

  @override
  Future<Map<String, dynamic>> uploadIncident(LocalIncident incident) async {
    final file = File(incident.localImagePath);
    if (!await file.exists()) {
      throw UploadException('Local image file not found on device at: ${incident.localImagePath}');
    }

    final fields = <String, String>{
      'citizen_rating': incident.citizenRating.toString(),
      'location_status': incident.locationStatus,
      'timestamp': incident.timestamp.toUtc().toIso8601String(),
      'client_incident_id': incident.localId,
    };

    if (incident.hasLocation) {
      fields['latitude'] = incident.latitude!.toString();
      fields['longitude'] = incident.longitude!.toString();
      if (incident.gpsAccuracy != null) {
        fields['gps_accuracy'] = incident.gpsAccuracy!.toString();
      }
    }

    try {
      final response = await _apiClient.postMultipart(
        ApiConstants.incidents,
        imageFile: file,
        fields: fields,
      );

      if (response is! Map<String, dynamic>) {
        throw UploadException('Invalid server response format.');
      }

      return response;
    } on ServerException catch (e) {
      throw UploadException(e.message, e.statusCode);
    }
  }
}
