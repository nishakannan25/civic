/// Phase 3 — Local Incident domain model.
///
/// Represents an incident stored in the device's persistent storage,
/// tracking its local lifecycle, synchronization queue state, retry history,
/// and mapping to the backend server record once uploaded.

import 'dart:convert';

/// Lifecycle statuses for local incidents in the sync queue.
class LocalIncidentStatus {
  /// Incident is currently being created on device
  static const String draft = 'DRAFT';

  /// Incident is complete and waiting for network to upload
  static const String pendingSync = 'PENDING_SYNC';

  /// Incident upload is currently in progress
  static const String uploading = 'UPLOADING';

  /// Incident was accepted and persisted by the backend server
  static const String uploaded = 'UPLOADED';

  /// Incident upload failed after maximum retry attempts (retained for user inspection/retry)
  static const String failed = 'FAILED';
}

class LocalIncident {
  /// Unique client-generated identifier (UUID format: e.g. "loc-xxxx-xxxx")
  final String localId;

  /// Backend server ID (null until successfully uploaded)
  final int? serverId;

  /// User ID who created the report
  final int userId;

  /// Persistent local path to the captured image in app storage
  final String localImagePath;

  /// Server URL of the uploaded image (null until uploaded)
  final String? imageUrl;

  /// Optional GPS latitude
  final double? latitude;

  /// Optional GPS longitude
  final double? longitude;

  /// Optional GPS accuracy in metres
  final double? gpsAccuracy;

  /// 'AVAILABLE' if GPS coordinates were captured, 'UNAVAILABLE' otherwise
  final String locationStatus;

  /// Time when the incident was captured by the citizen
  final DateTime timestamp;

  /// Citizen perceived severity (0 to 10)
  final int citizenRating;

  /// Sync queue status: DRAFT, PENDING_SYNC, UPLOADING, UPLOADED, FAILED
  final String status;

  /// Number of sync attempts performed
  final int syncAttempts;

  /// Timestamp of the last sync attempt
  final DateTime? lastSyncAttempt;

  /// Error message from the last failed sync attempt
  final String? lastSyncError;

  /// Local creation timestamp
  final DateTime createdAt;

  /// Local updated timestamp
  final DateTime updatedAt;

  const LocalIncident({
    required this.localId,
    this.serverId,
    this.userId = 0,
    required this.localImagePath,
    this.imageUrl,
    this.latitude,
    this.longitude,
    this.gpsAccuracy,
    required this.locationStatus,
    required this.timestamp,
    required this.citizenRating,
    required this.status,
    this.syncAttempts = 0,
    this.lastSyncAttempt,
    this.lastSyncError,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Human-friendly reference string for UI display
  String get referenceId {
    if (serverId != null) {
      return 'CIV-${createdAt.year}-${serverId.toString().padLeft(6, '0')}';
    }
    final shortId = localId.length > 8 ? localId.substring(0, 8).toUpperCase() : localId.toUpperCase();
    return 'LOCAL-$shortId';
  }

  /// Human-readable status label for the UI
  String get statusLabel {
    switch (status) {
      case LocalIncidentStatus.draft:
        return 'Draft';
      case LocalIncidentStatus.pendingSync:
        return 'Waiting to upload';
      case LocalIncidentStatus.uploading:
        return 'Uploading';
      case LocalIncidentStatus.uploaded:
        return 'Uploaded';
      case LocalIncidentStatus.failed:
        return 'Upload needs attention';
      default:
        return status;
    }
  }

  bool get isUploaded => status == LocalIncidentStatus.uploaded && serverId != null;
  bool get isPending => status == LocalIncidentStatus.pendingSync;
  bool get isUploading => status == LocalIncidentStatus.uploading;
  bool get isFailed => status == LocalIncidentStatus.failed;
  bool get hasLocation => locationStatus == 'AVAILABLE' && latitude != null && longitude != null;

  /// Copy with updated fields
  LocalIncident copyWith({
    String? localId,
    int? serverId,
    int? userId,
    String? localImagePath,
    String? imageUrl,
    double? latitude,
    double? longitude,
    double? gpsAccuracy,
    String? locationStatus,
    DateTime? timestamp,
    int? citizenRating,
    String? status,
    int? syncAttempts,
    DateTime? lastSyncAttempt,
    String? lastSyncError,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return LocalIncident(
      localId: localId ?? this.localId,
      serverId: serverId ?? this.serverId,
      userId: userId ?? this.userId,
      localImagePath: localImagePath ?? this.localImagePath,
      imageUrl: imageUrl ?? this.imageUrl,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      gpsAccuracy: gpsAccuracy ?? this.gpsAccuracy,
      locationStatus: locationStatus ?? this.locationStatus,
      timestamp: timestamp ?? this.timestamp,
      citizenRating: citizenRating ?? this.citizenRating,
      status: status ?? this.status,
      syncAttempts: syncAttempts ?? this.syncAttempts,
      lastSyncAttempt: lastSyncAttempt ?? this.lastSyncAttempt,
      lastSyncError: lastSyncError ?? this.lastSyncError,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  /// Serialize to a Map for database storage
  Map<String, dynamic> toMap() {
    return {
      'local_id': localId,
      'server_id': serverId,
      'user_id': userId,
      'local_image_path': localImagePath,
      'image_url': imageUrl,
      'latitude': latitude,
      'longitude': longitude,
      'gps_accuracy': gpsAccuracy,
      'location_status': locationStatus,
      'timestamp': timestamp.toUtc().toIso8601String(),
      'citizen_rating': citizenRating,
      'status': status,
      'sync_attempts': syncAttempts,
      'last_sync_attempt': lastSyncAttempt?.toUtc().toIso8601String(),
      'last_sync_error': lastSyncError,
      'created_at': createdAt.toUtc().toIso8601String(),
      'updated_at': updatedAt.toUtc().toIso8601String(),
    };
  }

  /// Construct from a database record Map
  factory LocalIncident.fromMap(Map<String, dynamic> map) {
    return LocalIncident(
      localId: map['local_id'] as String,
      serverId: map['server_id'] as int?,
      userId: map['user_id'] as int? ?? 0,
      localImagePath: map['local_image_path'] as String,
      imageUrl: map['image_url'] as String?,
      latitude: (map['latitude'] as num?)?.toDouble(),
      longitude: (map['longitude'] as num?)?.toDouble(),
      gpsAccuracy: (map['gps_accuracy'] as num?)?.toDouble(),
      locationStatus: map['location_status'] as String? ?? 'UNAVAILABLE',
      timestamp: DateTime.parse(map['timestamp'] as String),
      citizenRating: map['citizen_rating'] as int,
      status: map['status'] as String? ?? LocalIncidentStatus.pendingSync,
      syncAttempts: map['sync_attempts'] as int? ?? 0,
      lastSyncAttempt: map['last_sync_attempt'] != null ? DateTime.parse(map['last_sync_attempt'] as String) : null,
      lastSyncError: map['last_sync_error'] as String?,
      createdAt: DateTime.parse(map['created_at'] as String),
      updatedAt: DateTime.parse(map['updated_at'] as String),
    );
  }

  String toJson() => jsonEncode(toMap());
  factory LocalIncident.fromJson(String source) => LocalIncident.fromMap(jsonDecode(source) as Map<String, dynamic>);
}
