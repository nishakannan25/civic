/// Centralized AI issue taxonomy classes shared across mobile and backend.
class AiTaxonomy {
  // Phase 1 / Phase 4 Active Classes
  static const int pothole = 0;
  static const int openManhole = 1;
  static const int garbage = 2;

  // Future Phase Classes
  static const int flooding = 3;
  static const int brokenStreetlight = 4;
  static const int waterLeakage = 5;

  static String getLabel(int classId) {
    switch (classId) {
      case pothole:
        return 'Pothole';
      case openManhole:
        return 'Open Manhole';
      case garbage:
        return 'Garbage / Waste';
      case flooding:
        return 'Flooding';
      case brokenStreetlight:
        return 'Broken Streetlight';
      case waterLeakage:
        return 'Water Leakage';
      default:
        return 'Unknown Issue';
    }
  }
}
