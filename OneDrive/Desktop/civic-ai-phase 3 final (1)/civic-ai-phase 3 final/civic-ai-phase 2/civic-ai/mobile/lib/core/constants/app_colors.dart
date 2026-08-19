import 'package:flutter/material.dart';

/// Clean, high-contrast, accessible civic & emergency color palette.
class AppColors {
  // Primary Brand - Deep Civic Navy / Indigo
  static const Color primary = Color(0xFF1E3A8A);
  static const Color primaryLight = Color(0xFF3B82F6);
  static const Color primaryDark = Color(0xFF172554);

  // Emergency / SOS Actions - Distinct High-Visibility Crimson
  static const Color emergencyRed = Color(0xFFDC2626);
  static const Color emergencyRedLight = Color(0xFFEF4444);
  static const Color emergencyRedDark = Color(0xFF991B1B);

  // Secondary / Accent - Energetic Amber / Warning
  static const Color warning = Color(0xFFF59E0B);
  static const Color success = Color(0xFF10B981);
  static const Color info = Color(0xFF0284C7);

  // Background & Surfaces (Accessible Dark Mode Viewport + Light UI)
  static const Color background = Color(0xFFF8FAFC);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cameraViewport = Color(0xFF0F172A);
  static const Color cameraOverlay = Color(0x66000000);

  // Neutral / Typography
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textLight = Color(0xFFF1F5F9);
  static const Color border = Color(0xFFE2E8F0);
  static const Color divider = Color(0xFFCBD5E1);

  // Status Colors
  static const Color statusDraft = Color(0xFF94A3B8);
  static const Color statusPending = Color(0xFFEAB308);
  static const Color statusProcessing = Color(0xFF3B82F6);
  static const Color statusResolved = Color(0xFF22C55E);
  static const Color statusClosed = Color(0xFF64748B);
  static const Color statusCritical = Color(0xFFDC2626);
}
