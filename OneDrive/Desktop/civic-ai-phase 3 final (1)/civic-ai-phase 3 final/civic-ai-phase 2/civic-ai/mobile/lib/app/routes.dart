import 'package:flutter/material.dart';
import '../features/camera/presentation/camera_screen.dart';
import '../features/incidents/screens/pending_incidents_screen.dart';
import '../features/community/community_placeholder.dart';
import '../features/profile/profile_placeholder.dart';
import '../features/settings/settings_placeholder.dart';
import '../core/constants/app_strings.dart';
import '../core/constants/app_colors.dart';

/// Named route constants for Phase 3.
class AppRoutes {
  static const String initial = '/';
  static const String incidentPreview = '/incident-preview';
  static const String incidentSuccess = '/incident-success';
  static const String incidents = '/incidents';
  static const String savedReports = '/saved-reports';
  static const String verify = '/verify';
  static const String profile = '/profile';
  static const String settings = '/settings';

  static Map<String, WidgetBuilder> get routes => {
        initial: (context) => const MainNavigationShell(),
        incidents: (context) => const PendingIncidentsScreen(),
        savedReports: (context) => const PendingIncidentsScreen(),
        verify: (context) => const CommunityPlaceholderScreen(),
        profile: (context) => const ProfilePlaceholderScreen(),
        settings: (context) => const SettingsPlaceholderScreen(),
      };
}

/// Main navigation shell with bottom navigation bar.
/// The camera tab is always the first tab (camera-first design).
class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;

  final List<Widget> _pages = const [
    CameraScreen(),
    PendingIncidentsScreen(),
    CommunityPlaceholderScreen(),
    ProfilePlaceholderScreen(),
    SettingsPlaceholderScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _pages,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.camera_alt_outlined),
            activeIcon: Icon(Icons.camera_alt, color: AppColors.primary),
            label: AppStrings.navCamera,
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.list_alt_outlined),
            activeIcon: Icon(Icons.list_alt, color: AppColors.primary),
            label: AppStrings.navIncidents,
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.how_to_reg_outlined),
            activeIcon: Icon(Icons.how_to_reg, color: AppColors.primary),
            label: AppStrings.navVerify,
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person, color: AppColors.primary),
            label: AppStrings.navProfile,
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings, color: AppColors.primary),
            label: AppStrings.navSettings,
          ),
        ],
      ),
    );
  }
}
