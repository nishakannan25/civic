/// Core application exceptions for Civic AI mobile.

class ServerException implements Exception {
  final String message;
  final int? statusCode;
  ServerException(this.message, [this.statusCode]);
  @override
  String toString() => 'ServerException(status: $statusCode, message: $message)';
}

class NetworkException implements Exception {
  final String message;
  NetworkException([this.message = 'No network connectivity. Check connection.']);
  @override
  String toString() => 'NetworkException: $message';
}

class AuthException implements Exception {
  final String message;
  AuthException(this.message);
  @override
  String toString() => 'AuthException: $message';
}

class CacheException implements Exception {
  final String message;
  CacheException(this.message);
  @override
  String toString() => 'CacheException: $message';
}

// ── Phase 2 exceptions ────────────────────────────────────────────────────────

/// Thrown when camera permission is denied or camera cannot initialise.
class CameraException implements Exception {
  final String message;
  CameraException(this.message);
  @override
  String toString() => 'CameraException: $message';
}

/// Thrown when GPS permission is denied or location cannot be obtained.
class LocationException implements Exception {
  final String message;
  LocationException(this.message);
  @override
  String toString() => 'LocationException: $message';
}

/// Thrown when the image upload to the backend fails.
class UploadException implements Exception {
  final String message;
  final int? statusCode;
  UploadException(this.message, [this.statusCode]);
  @override
  String toString() => 'UploadException(status: $statusCode, message: $message)';
}
