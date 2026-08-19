/// Push notification interface placeholder for Phase 8.
abstract class INotificationService {
  Future<void> initialize();
  Future<void> showLocalNotification(String title, String body);
}

class NotificationPlaceholderService implements INotificationService {
  @override
  Future<void> initialize() async {}

  @override
  Future<void> showLocalNotification(String title, String body) async {}
}
