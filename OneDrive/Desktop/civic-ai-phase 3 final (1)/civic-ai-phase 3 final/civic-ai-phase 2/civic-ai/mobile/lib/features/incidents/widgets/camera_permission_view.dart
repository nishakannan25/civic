/// Camera Permission UI — shown when permission is denied or permanently denied.

import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_strings.dart';

class CameraPermissionView extends StatelessWidget {
  /// True when permission is permanently denied and the user must go to Settings.
  final bool isPermanentlyDenied;
  final VoidCallback onRetry;

  const CameraPermissionView({
    super.key,
    required this.isPermanentlyDenied,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.background,
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Icon
              Container(
                padding: const EdgeInsets.all(28),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.08),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.camera_alt_outlined,
                  size: 64,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(height: 32),

              // Title
              Text(
                isPermanentlyDenied
                    ? AppStrings.cameraPermissionPermanentlyDenied
                    : AppStrings.cameraPermissionRequired,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 12),

              Text(
                'Camera access lets you photograph civic problems in your community.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 40),

              // Action button
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    if (isPermanentlyDenied) {
                      await openAppSettings();
                    } else {
                      onRetry();
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                    elevation: 3,
                  ),
                  icon: Icon(
                    isPermanentlyDenied ? Icons.settings_outlined : Icons.camera_alt,
                    size: 22,
                  ),
                  label: Text(
                    isPermanentlyDenied ? AppStrings.openSettings : AppStrings.grantPermission,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
