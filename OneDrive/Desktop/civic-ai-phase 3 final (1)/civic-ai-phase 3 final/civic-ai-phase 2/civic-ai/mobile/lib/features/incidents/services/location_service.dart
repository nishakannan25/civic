/// Phase 2 Location Service — GPS capture with full permission handling.
///
/// Captures the device location ONCE per incident creation.
/// Does NOT run background location tracking (privacy-by-design).
///
/// Compatible with Phase 3: LocationCaptureResult carries all fields
/// needed to retry the location capture in the offline sync queue.

import 'dart:async';
import 'package:geolocator/geolocator.dart';
import '../models/location_data.dart';

class LocationService {
  /// Timeout for a single location fix attempt.
  static const Duration _locationTimeout = Duration(seconds: 10);

  /// Attempt to capture the current device location for an incident.
  ///
  /// Handles all permission states and service-disabled states gracefully.
  /// Never throws — always returns a [LocationCaptureResult].
  Future<LocationCaptureResult> captureLocation() async {
    // 1. Check if location services are enabled on the device
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      return LocationCaptureResult.unavailable(
        'Location services are disabled on this device.',
      );
    }

    // 2. Check / request location permission
    LocationPermission permission = await Geolocator.checkPermission();

    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        return LocationCaptureResult.unavailable(
          'Location permission was denied.',
        );
      }
    }

    if (permission == LocationPermission.deniedForever) {
      return LocationCaptureResult.unavailable(
        'Location permission is permanently denied. '
        'Enable it in device Settings to attach your location.',
      );
    }

    // 3. Attempt to get the position with a timeout
    try {
      final position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      ).timeout(_locationTimeout);

      return LocationCaptureResult.available(
        LocationData(
          latitude: position.latitude,
          longitude: position.longitude,
          accuracy: position.accuracy,
          timestamp: DateTime.now().toUtc(),
        ),
      );
    } on TimeoutException catch (_) {
      // Try one more time with lower accuracy before giving up
      try {
        final position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.medium,
        ).timeout(const Duration(seconds: 5));

        return LocationCaptureResult.available(
          LocationData(
            latitude: position.latitude,
            longitude: position.longitude,
            accuracy: position.accuracy,
            timestamp: DateTime.now().toUtc(),
          ),
        );
      } catch (_) {
        return LocationCaptureResult.unavailable(
          'Location timed out. GPS may be unavailable indoors.',
        );
      }
    } catch (e) {
      return LocationCaptureResult.unavailable(
        'Could not determine location: ${e.runtimeType}',
      );
    }
  }
}
