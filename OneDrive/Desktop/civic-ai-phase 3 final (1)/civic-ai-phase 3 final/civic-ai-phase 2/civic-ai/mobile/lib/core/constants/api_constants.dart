/// REST API endpoints and contract constants.
class ApiConstants {
  static const String health = '/health';
  
  // Authentication
  static const String authRegister = '/auth/register';
  static const String authLogin = '/auth/login';

  // Users
  static const String usersMe = '/users/me';

  // Incidents
  static const String incidents = '/incidents';
  static String incidentDetail(int id) => '/incidents/$id';

  // Future Phase Endpoints
  static const String verifications = '/community/verifications';
  static const String notifications = '/notifications';
  static const String sos = '/sos';
  static const String departments = '/departments';
}
