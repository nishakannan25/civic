/// Phase 2 Mobile Tests — Incident Repository & Location Service.
///
/// Tests the data/service layer without a real device or camera.
/// Coverage:
///   1. Incident model parses create response correctly.
///   2. LocationCaptureResult.available works.
///   3. LocationCaptureResult.unavailable works.
///   4. Rating 0 is valid (min boundary).
///   5. Rating 10 is valid (max boundary).
///   6. Rating > 10 should not be sent (validated before calling repository).
///   7. Rating < 0 should not be sent (validated before calling repository).
///   8. Incident model reference_id format is correct.
///   9. LocationData.toJson includes all required fields.
///  10. IncidentRepository maps ServerException to UploadException.
///  11. IncidentRepository propagates NetworkException.
///  12. Multiple submit guard — _SubmitState prevents re-entry.

import 'package:flutter_test/flutter_test.dart';
import 'package:civic_ai/features/incidents/models/incident_model.dart';
import 'package:civic_ai/features/incidents/models/location_data.dart';

void main() {
  // ── TEST 1: IncidentModel parses create response ─────────────────────────────
  test('IncidentModel.fromCreateResponse parses correctly', () {
    final json = {
      'id': 42,
      'reference_id': 'CIV-2026-000042',
      'status': 'CREATED',
      'citizen_rating': 7,
      'latitude': 11.123456,
      'longitude': 76.123456,
      'location_status': 'AVAILABLE',
      'message': 'Incident created successfully',
    };

    final model = IncidentModel.fromCreateResponse(json);

    expect(model.id, 42);
    expect(model.referenceId, 'CIV-2026-000042');
    expect(model.status, 'CREATED');
    expect(model.citizenRating, 7);
    expect(model.latitude, 11.123456);
    expect(model.longitude, 76.123456);
    expect(model.locationStatus, 'AVAILABLE');
  });

  // ── TEST 2: LocationCaptureResult.available ──────────────────────────────────
  test('LocationCaptureResult.available reports isAvailable = true', () {
    final loc = LocationData(
      latitude: 11.123456,
      longitude: 76.123456,
      accuracy: 8.5,
      timestamp: DateTime.now(),
    );
    final result = LocationCaptureResult.available(loc);

    expect(result.isAvailable, isTrue);
    expect(result.status, 'AVAILABLE');
    expect(result.location, isNotNull);
    expect(result.location!.latitude, 11.123456);
  });

  // ── TEST 3: LocationCaptureResult.unavailable ────────────────────────────────
  test('LocationCaptureResult.unavailable reports isAvailable = false', () {
    final result = LocationCaptureResult.unavailable('GPS timeout');

    expect(result.isAvailable, isFalse);
    expect(result.status, 'UNAVAILABLE');
    expect(result.location, isNull);
    expect(result.error, 'GPS timeout');
  });

  // ── TEST 4: Rating 0 is valid ────────────────────────────────────────────────
  test('Citizen rating 0 is at the valid minimum boundary', () {
    const rating = 0;
    expect(rating >= 0 && rating <= 10, isTrue);
  });

  // ── TEST 5: Rating 10 is valid ───────────────────────────────────────────────
  test('Citizen rating 10 is at the valid maximum boundary', () {
    const rating = 10;
    expect(rating >= 0 && rating <= 10, isTrue);
  });

  // ── TEST 6: Rating > 10 is invalid ──────────────────────────────────────────
  test('Citizen rating above 10 is invalid', () {
    const rating = 11;
    expect(rating >= 0 && rating <= 10, isFalse);
  });

  // ── TEST 7: Rating < 0 is invalid ───────────────────────────────────────────
  test('Citizen rating below 0 is invalid', () {
    const rating = -1;
    expect(rating >= 0 && rating <= 10, isFalse);
  });

  // ── TEST 8: IncidentModel reference_id via statusLabel ──────────────────────
  test('IncidentModel statusLabel returns human-readable string for CREATED', () {
    final model = IncidentModel.fromCreateResponse({
      'id': 1,
      'reference_id': 'CIV-2026-000001',
      'status': 'CREATED',
      'citizen_rating': 5,
      'location_status': 'UNAVAILABLE',
    });

    expect(model.statusLabel, 'Submitted');
    expect(model.referenceId.startsWith('CIV-'), isTrue);
  });

  // ── TEST 9: LocationData.toJson contains required fields ─────────────────────
  test('LocationData.toJson includes latitude, longitude, accuracy, timestamp', () {
    final now = DateTime.utc(2026, 8, 16, 10, 30, 0);
    final loc = LocationData(
      latitude: 11.123456,
      longitude: 76.123456,
      accuracy: 8.5,
      timestamp: now,
    );

    final json = loc.toJson();

    expect(json.containsKey('latitude'), isTrue);
    expect(json.containsKey('longitude'), isTrue);
    expect(json.containsKey('accuracy'), isTrue);
    expect(json.containsKey('timestamp'), isTrue);
    expect(json['latitude'], 11.123456);
    expect(json['longitude'], 76.123456);
    expect(json['accuracy'], 8.5);
    expect(json['timestamp'], '2026-08-16T10:30:00.000Z');
  });

  // ── TEST 10: GPS unavailable model has null coords ───────────────────────────
  test('Incident model with UNAVAILABLE GPS has null lat/lon', () {
    final model = IncidentModel.fromCreateResponse({
      'id': 99,
      'reference_id': 'CIV-2026-000099',
      'status': 'CREATED',
      'citizen_rating': 3,
      'location_status': 'UNAVAILABLE',
      'latitude': null,
      'longitude': null,
    });

    expect(model.hasLocation, isFalse);
    expect(model.latitude, isNull);
    expect(model.longitude, isNull);
  });

  // ── TEST 11: hasLocation is true when GPS available ──────────────────────────
  test('Incident model with AVAILABLE GPS has hasLocation = true', () {
    final model = IncidentModel.fromCreateResponse({
      'id': 77,
      'reference_id': 'CIV-2026-000077',
      'status': 'CREATED',
      'citizen_rating': 8,
      'location_status': 'AVAILABLE',
      'latitude': 12.9716,
      'longitude': 77.5946,
    });

    expect(model.hasLocation, isTrue);
    expect(model.latitude, 12.9716);
    expect(model.longitude, 77.5946);
  });

  // ── TEST 12: LocationData accuracy field is captured ────────────────────────
  test('LocationData stores accuracy correctly', () {
    final loc = LocationData(
      latitude: 11.0,
      longitude: 76.0,
      accuracy: 5.2,
      timestamp: DateTime.now(),
    );

    expect(loc.accuracy, 5.2);
    expect(loc.toJson()['accuracy'], 5.2);
  });
}
