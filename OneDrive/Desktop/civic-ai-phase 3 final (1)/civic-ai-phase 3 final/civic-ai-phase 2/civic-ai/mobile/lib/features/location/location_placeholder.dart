/// Location service interface placeholder for Phase 6.
abstract class ILocationService {
  Future<Map<String, double>> getCurrentCoordinates();
  Future<double> getAccuracy();
}

class LocationPlaceholderService implements ILocationService {
  @override
  Future<Map<String, double>> getCurrentCoordinates() async {
    // Placeholder coordinates (Bengaluru default: 12.9716, 77.5946)
    return {'latitude': 12.9716, 'longitude': 77.5946};
  }

  @override
  Future<double> getAccuracy() async {
    return 10.0;
  }
}
