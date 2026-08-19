import 'package:flutter/material.dart';
import 'app/app.dart';
import 'core/connectivity/connectivity_service.dart';
import 'core/storage/local_database.dart';
import 'features/incidents/services/sync_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Phase 3: Initialize persistent local database on app startup
  await LocalDatabase().init();

  // Phase 3: Start real-time network connectivity monitoring
  ConnectivityService().startMonitoring();

  // Phase 3: Initialize background sync service (checks & syncs pending reports on startup and connection return)
  SyncService().init();

  runApp(const CivicAiApp());
}
