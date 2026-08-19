/// User-facing failure representations.
abstract class Failure {
  final String message;
  const Failure(this.message);
}

class ServerFailure extends Failure {
  final int? statusCode;
  const ServerFailure(String message, [this.statusCode]) : super(message);
}

class NetworkFailure extends Failure {
  const NetworkFailure([String message = 'Network connection failed']) : super(message);
}

class AuthFailure extends Failure {
  const AuthFailure(String message) : super(message);
}
