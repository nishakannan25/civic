/// User data model matching backend schema (excluding password_hash).
class UserModel {
  final int id;
  final String name;
  final String email;
  final String? phone;
  final String role;
  final int points;
  final double reputationScore;
  final String createdAt;

  UserModel({
    required this.id,
    required this.name,
    required this.email,
    this.phone,
    required this.role,
    this.points = 0,
    this.reputationScore = 5.0,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      name: json['name'] as String,
      email: json['email'] as String,
      phone: json['phone'] as String?,
      role: json['role'] as String? ?? 'citizen',
      points: json['points'] as int? ?? 0,
      reputationScore: (json['reputation_score'] as num?)?.toDouble() ?? 5.0,
      createdAt: json['created_at'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'phone': phone,
      'role': role,
      'points': points,
      'reputation_score': reputationScore,
      'created_at': createdAt,
    };
  }
}
