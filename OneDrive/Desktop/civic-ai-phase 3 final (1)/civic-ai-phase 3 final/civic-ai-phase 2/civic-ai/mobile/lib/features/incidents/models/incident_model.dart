/// Phase 2 / Phase 6 — Incident domain model for the mobile client.
///
/// This is a pure Dart model (no Flutter dependency).
/// It maps to the backend Incident table and the POST /incidents response.
///
/// Phase 6 additions:
///   - riskScore  : 0–100 risk score from Risk Engine (nullable until assessed).
///   - riskLevel  : LOW | MEDIUM | HIGH | CRITICAL (nullable until assessed).
///   - priority   : LOW | NORMAL | HIGH | URGENT (nullable until assessed).
class IncidentModel {
  final int id;
  final String referenceId;
  final int userId;
  final String? imageUrl;
  final double? latitude;
  final double? longitude;
  final double? gpsAccuracy;
  final String locationStatus;
  final DateTime timestamp;
  final int citizenRating;
  final String status;
  final DateTime createdAt;

  // Phase 6: Risk Engine fields (null until POST /incidents/{id}/risk-assessment is called)
  final double? riskScore;
  final String? riskLevel;
  final String? priority;

  const IncidentModel({
    required this.id,
    required this.referenceId,
    required this.userId,
    this.imageUrl,
    this.latitude,
    this.longitude,
    this.gpsAccuracy,
    required this.locationStatus,
    required this.timestamp,
    required this.citizenRating,
    required this.status,
    required this.createdAt,
    // Phase 6
    this.riskScore,
    this.riskLevel,
    this.priority,
  });

  /// Construct from the slim POST /incidents response body.
  factory IncidentModel.fromCreateResponse(Map<String, dynamic> json) {
    return IncidentModel(
      id: json['id'] as int,
      referenceId: json['reference_id'] as String? ?? 'CIV-UNKNOWN',
      userId: 0, // Not returned in slim response; populated from auth context
      imageUrl: json['image_url'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      gpsAccuracy: null,
      locationStatus: json['location_status'] as String? ?? 'UNAVAILABLE',
      timestamp: DateTime.now().toUtc(),
      citizenRating: json['citizen_rating'] as int,
      status: json['status'] as String? ?? 'CREATED',
      createdAt: DateTime.now().toUtc(),
      // Phase 6: parse risk fields when present in response
      riskScore: (json['risk_score'] as num?)?.toDouble(),
      riskLevel: json['risk_level'] as String?,
      priority: json['priority'] as String?,
    );
  }

  /// Whether this incident has a completed risk assessment.
  bool get hasRiskAssessment => riskScore != null && riskLevel != null;

  /// Human-friendly status label for UI display.
  String get statusLabel {
    switch (status) {
      case 'CREATED':
        return 'Submitted';
      case 'DRAFT':
        return 'Draft';
      case 'RESOLVED':
        return 'Resolved';
      case 'RISK_ASSESSED':
        return 'Risk Assessed';
      default:
        return status;
    }
  }

  bool get hasLocation =>
      locationStatus == 'AVAILABLE' && latitude != null && longitude != null;
}
