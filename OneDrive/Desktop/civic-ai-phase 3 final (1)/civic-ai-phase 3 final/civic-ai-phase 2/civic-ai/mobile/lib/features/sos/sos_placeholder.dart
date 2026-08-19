/// SOS emergency service interface placeholder for Phase 10.
abstract class ISosService {
  Future<void> triggerSos({required double latitude, required double longitude, String? reason});
}

class SosPlaceholderService implements ISosService {
  @override
  Future<void> triggerSos({required double latitude, required double longitude, String? reason}) async {}
}
