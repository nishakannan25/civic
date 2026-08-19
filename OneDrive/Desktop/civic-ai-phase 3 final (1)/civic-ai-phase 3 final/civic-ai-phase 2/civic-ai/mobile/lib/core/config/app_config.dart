/// Application environment configuration for Civic AI mobile client.
class AppConfig {
  static const String appName = 'Civic AI';
  static const String appVersion = '0.2.0';
  static const String packageName = 'com.civicai.app';

  /// Base URL for FastAPI Backend.
  ///
  /// Development Defaults:
  /// - Android Emulator: 'http://10.0.2.2:8000'
  /// - iOS Simulator / macOS / Web: 'http://127.0.0.1:8000'
  /// - Physical Device: 'http://<YOUR_LOCAL_IP>:8000' (e.g. http://192.168.1.100:8000)
  /// - Production: Configure via environment / build flavor
  static String apiBaseUrl = const String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  /// Standard API request timeout (GET, JSON POST, etc.)
  static const Duration requestTimeout = Duration(seconds: 15);

  /// Extended timeout for multipart image uploads (Phase 2)
  static const Duration uploadTimeout = Duration(seconds: 30);

  // ── Phase 3: Synchronization & Retry Configurations ──────────────────────────
  /// Maximum number of upload retry attempts before marking an incident as FAILED
  static const int syncMaxRetries = 4;

  /// Base backoff time in seconds for exponential backoff (e.g. 2s, 4s, 8s, 16s)
  static const int syncInitialBackoffSeconds = 2;

  /// Maximum cap for backoff delay
  static const int syncMaxBackoffSeconds = 30;

  /// Allows dynamic override of API base URL during development
  static void setBaseUrl(String newUrl) {
    apiBaseUrl = newUrl;
  }
}
