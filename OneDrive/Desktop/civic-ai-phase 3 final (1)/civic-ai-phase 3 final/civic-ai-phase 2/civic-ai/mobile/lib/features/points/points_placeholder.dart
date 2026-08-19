/// Citizen points & reputation interface placeholder for Phase 9.
abstract class IPointsService {
  Future<int> fetchUserPoints(int userId);
}

class PointsPlaceholderService implements IPointsService {
  @override
  Future<int> fetchUserPoints(int userId) async {
    return 0;
  }
}
