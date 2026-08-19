import 'package:flutter/material.dart';
import 'routes.dart';
import 'theme.dart';
import '../core/constants/app_strings.dart';

/// Root application widget for Civic AI.
class CivicAiApp extends StatelessWidget {
  const CivicAiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppStrings.appTitle,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      initialRoute: AppRoutes.initial,
      routes: AppRoutes.routes,
    );
  }
}
