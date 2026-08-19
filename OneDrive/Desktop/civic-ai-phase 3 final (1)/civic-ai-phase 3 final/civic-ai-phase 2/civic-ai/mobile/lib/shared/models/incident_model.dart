/// Incident data model matching backend schema.
class IncidentModel {
  final int id;
  final int userId;
  final String? imageUrl;
  final double latitude;
  final double longitude;
  final double? gpsAccuracy;
  final String timestamp;
  final int? citizenRating;
  final int? aiIssueType;
  final double? aiConfidence;
  final int? aiSeverity;
  final int communityYes;
  final int communityNo;
  final int communityUnknown;
  final double? riskScore;
  final String? riskLevel;
  final String status;
  final String createdAt;
  final String? updatedAt;

  IncidentModel({
    required this.id,
    required this.userId,
    this.imageUrl,
    required this.latitude,
    required this.longitude,
    this.gpsAccuracy,
    required this.timestamp,
    this.citizenRating,
    this.aiIssueType,
    this.aiConfidence,
    this.aiSeverity,
    this.communityYes = 0,
    this.communityNo = 0,
    this.communityUnknown = 0,
    this.riskScore,
    this.riskLevel,
    required this.status,
    required this.createdAt,
    this.updatedAt,
  });

  factory IncidentModel.fromJson(Map<String, dynamic> json) {
    return IncidentModel(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      imageUrl: json['image_url'] as String?,
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      gpsAccuracy: (json['gps_accuracy'] as num?)?.toDouble(),
      timestamp: json['timestamp'] as String,
      citizenRating: json['citizen_rating'] as int?,
      aiIssueType: json['ai_issue_type'] as int?,
      aiConfidence: (json['ai_confidence'] as num?)?.toDouble(),
      aiSeverity: json['ai_severity'] as int?,
      communityYes: json['community_yes'] as int? ?? 0,
      communityNo: json['community_no'] as int? ?? 0,
      communityUnknown: json['community_unknown'] as int? ?? 0,
      riskScore: (json['risk_score'] as num?)?.toDouble(),
      riskLevel: json['risk_level'] as String?,
      status: json['status'] as String? ?? 'DRAFT',
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'image_url': imageUrl,
      'latitude': latitude,
      'longitude': longitude,
      'gps_accuracy': gpsAccuracy,
      'timestamp': timestamp,
      'citizen_rating': citizenRating,
      'ai_issue_type': aiIssueType,
      'ai_confidence': aiConfidence,
      'ai_severity': aiSeverity,
      'community_yes': communityYes,
      'community_no': communityNo,
      'community_unknown': communityUnknown,
      'risk_score': riskScore,
      'risk_level': riskLevel,
      'status': status,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }
}
