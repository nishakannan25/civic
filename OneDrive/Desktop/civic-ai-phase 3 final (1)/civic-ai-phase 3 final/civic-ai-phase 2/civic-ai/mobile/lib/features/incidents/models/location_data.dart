/// GPS/Location capture result for Phase 2 incident creation.
///
/// Keeps location data in a typed container so the camera/capture logic
/// never needs to know about raw geolocator internals.
class LocationData {
  final double latitude;
  final double longitude;
  final double accuracy;
  final DateTime timestamp;

  const LocationData({
    required this.latitude,
    required this.longitude,
    required this.accuracy,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() => {
        'latitude': latitude,
        'longitude': longitude,
        'accuracy': accuracy,
        'timestamp': timestamp.toUtc().toIso8601String(),
      };

  @override
  String toString() =>
      'LocationData(lat: $latitude, lon: $longitude, acc: ${accuracy.toStringAsFixed(1)}m)';
}

/// Represents the result of a GPS capture attempt.
///
/// Either [LocationData] is present (success) or [error] explains why it failed.
/// Phase 3 can use [LocationCaptureResult.status] to decide whether to queue a retry.
class LocationCaptureResult {
  final LocationData? location;
  final String status; // 'AVAILABLE' | 'UNAVAILABLE'
  final String? error;

  const LocationCaptureResult._({
    this.location,
    required this.status,
    this.error,
  });

  factory LocationCaptureResult.available(LocationData location) {
    return LocationCaptureResult._(
      location: location,
      status: 'AVAILABLE',
    );
  }

  factory LocationCaptureResult.unavailable(String reason) {
    return LocationCaptureResult._(
      location: null,
      status: 'UNAVAILABLE',
      error: reason,
    );
  }

  bool get isAvailable => status == 'AVAILABLE' && location != null;
}
