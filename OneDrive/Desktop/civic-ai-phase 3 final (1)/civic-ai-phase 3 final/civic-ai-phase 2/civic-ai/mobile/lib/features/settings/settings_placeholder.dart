import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_strings.dart';
import '../../core/config/app_config.dart';

class SettingsPlaceholderScreen extends StatelessWidget {
  const SettingsPlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            elevation: 0,
            color: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: const BorderSide(color: AppColors.border),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Environment Configuration',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 12),
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Backend API URL', style: TextStyle(fontSize: 14)),
                    subtitle: Text(
                      AppConfig.apiBaseUrl,
                      style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.w600),
                    ),
                    leading: const Icon(Icons.cloud_sync_outlined, color: AppColors.primary),
                  ),
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('App Version', style: TextStyle(fontSize: 14)),
                    subtitle: const Text('v0.1.0 (Phase 1 Prototype)'),
                    leading: const Icon(Icons.info_outline, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            elevation: 0,
            color: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: const BorderSide(color: AppColors.border),
            ),
            child: const Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Icon(Icons.tune_rounded, size: 40, color: AppColors.textSecondary),
                  SizedBox(height: 10),
                  Text(
                    AppStrings.phase2Settings,
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
