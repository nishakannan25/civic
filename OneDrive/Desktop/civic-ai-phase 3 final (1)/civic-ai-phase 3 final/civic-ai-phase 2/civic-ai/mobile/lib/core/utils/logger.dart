/// Simple logger utility for mobile client.
class AppLogger {
  static void d(String message) {
    // ignore: avoid_print
    print('[DEBUG] [CivicAI] $message');
  }

  static void e(String message, [dynamic error, StackTrace? stackTrace]) {
    // ignore: avoid_print
    print('[ERROR] [CivicAI] $message | Error: $error');
  }
}
