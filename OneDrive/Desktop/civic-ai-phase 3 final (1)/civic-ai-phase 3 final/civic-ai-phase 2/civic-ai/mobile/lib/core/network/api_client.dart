import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../errors/exceptions.dart';

/// Lightweight HTTP Client for Civic AI backend communication.
///
/// Phase 2 additions:
/// - [postMultipart] for image + form-data uploads (POST /incidents)
/// - Auth token management carried over from Phase 1
class ApiClient {
  final http.Client _httpClient;
  String? _authToken;

  ApiClient({http.Client? httpClient}) : _httpClient = httpClient ?? http.Client();

  void setAuthToken(String token) => _authToken = token;
  void clearAuthToken() => _authToken = null;
  bool get isAuthenticated => _authToken != null;

  Map<String, String> _jsonHeaders() {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    return headers;
  }

  Map<String, String> _authHeaders() {
    final headers = <String, String>{'Accept': 'application/json'};
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    return headers;
  }

  // ── JSON Requests ────────────────────────────────────────────────────────────

  Future<dynamic> get(String endpoint) async {
    try {
      final uri = Uri.parse('${AppConfig.apiBaseUrl}$endpoint');
      final response = await _httpClient
          .get(uri, headers: _jsonHeaders())
          .timeout(AppConfig.requestTimeout);
      return _processResponse(response);
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException(e.toString());
    }
  }

  Future<dynamic> post(String endpoint, Map<String, dynamic> body) async {
    try {
      final uri = Uri.parse('${AppConfig.apiBaseUrl}$endpoint');
      final response = await _httpClient
          .post(uri, headers: _jsonHeaders(), body: jsonEncode(body))
          .timeout(AppConfig.requestTimeout);
      return _processResponse(response);
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException(e.toString());
    }
  }

  Future<dynamic> patch(String endpoint, Map<String, dynamic> body) async {
    try {
      final uri = Uri.parse('${AppConfig.apiBaseUrl}$endpoint');
      final response = await _httpClient
          .patch(uri, headers: _jsonHeaders(), body: jsonEncode(body))
          .timeout(AppConfig.requestTimeout);
      return _processResponse(response);
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException(e.toString());
    }
  }

  // ── Phase 2: Multipart Upload ────────────────────────────────────────────────

  /// Send a multipart/form-data POST request with an image file and form fields.
  ///
  /// Used for POST /incidents (Phase 2 incident creation).
  ///
  /// [imageFile] — the captured image file from the camera.
  /// [fields]    — form fields (citizen_rating, location_status, lat, lon, etc.)
  Future<dynamic> postMultipart(
    String endpoint, {
    required File imageFile,
    required Map<String, String> fields,
  }) async {
    try {
      final uri = Uri.parse('${AppConfig.apiBaseUrl}$endpoint');
      final request = http.MultipartRequest('POST', uri);

      // Attach auth header
      request.headers.addAll(_authHeaders());

      // Attach form fields
      request.fields.addAll(fields);

      // Attach image file
      final mimeType = _detectMimeType(imageFile.path);
      final multipartFile = await http.MultipartFile.fromPath(
        'image',
        imageFile.path,
        contentType: http.MediaType.parse(mimeType),
      );
      request.files.add(multipartFile);

      // Send with timeout
      final streamedResponse = await request.send().timeout(AppConfig.uploadTimeout);
      final response = await http.Response.fromStream(streamedResponse);
      return _processResponse(response);
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException(e.toString());
    }
  }

  // ── Internal ─────────────────────────────────────────────────────────────────

  dynamic _processResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    } else if (response.statusCode == 401) {
      String msg = 'Authentication failed. Please log in again.';
      try {
        final body = jsonDecode(response.body);
        if (body is Map && body.containsKey('detail')) msg = body['detail'].toString();
      } catch (_) {}
      throw ServerException(msg, response.statusCode);
    } else {
      String errorMessage = 'Request failed with status: ${response.statusCode}';
      try {
        final body = jsonDecode(response.body);
        if (body is Map && body.containsKey('detail')) {
          errorMessage = body['detail'].toString();
        }
      } catch (_) {}
      throw ServerException(errorMessage, response.statusCode);
    }
  }

  String _detectMimeType(String filePath) {
    final lower = filePath.toLowerCase();
    if (lower.endsWith('.png')) return 'image/png';
    return 'image/jpeg'; // default
  }
}
