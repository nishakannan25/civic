/// Phase 2 / Phase 6 — Incident Success Screen.
///
/// Displayed after a successful incident submission.
/// Shows the incident reference ID (e.g. CIV-2026-000123) and a
/// thank-you message. Provides a button to report another problem.
///
/// Phase 6: If the incident has a risk assessment attached (riskLevel, riskScore,
/// priority), a Risk Assessment card is displayed beneath the reference card.

import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_strings.dart';
import '../models/incident_model.dart';

class IncidentSuccessScreen extends StatelessWidget {
  final IncidentModel incident;
  final bool isOffline;

  const IncidentSuccessScreen({
    super.key,
    required this.incident,
    this.isOffline = false,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Success animation / icon
              _buildSuccessIcon(),

              const SizedBox(height: 32),

              // Headline
              Text(
                isOffline ? AppStrings.incidentSavedOffline : AppStrings.incidentSubmitted,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textPrimary,
                  letterSpacing: 0.3,
                ),
              ),

              const SizedBox(height: 12),

              // Subtitle / message
              Text(
                isOffline
                    ? AppStrings.incidentSavedOfflineSubtitle
                    : AppStrings.thankYouMessage,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 15,
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
              ),

              const SizedBox(height: 36),

              // Incident Reference Card
              _buildReferenceCard(),

              // Phase 6: Risk Assessment Card — shown only when risk data is available
              if (incident.hasRiskAssessment) ...[
                const SizedBox(height: 20),
                _buildRiskAssessmentCard(),
              ],

              const SizedBox(height: 48),

              // Report Another Problem button
              SizedBox(
                width: double.infinity,
                height: 60,
                child: ElevatedButton.icon(
                  onPressed: () {
                    // Pop back to the camera screen (root)
                    Navigator.of(context).popUntil((route) => route.isFirst);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    elevation: 4,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  icon: const Icon(Icons.camera_alt, size: 22),
                  label: const Text(
                    AppStrings.reportNewProblem,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.8,
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

  Widget _buildSuccessIcon() {
    final color = isOffline ? AppColors.warning : AppColors.success;
    return Container(
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.2),
            blurRadius: 30,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Icon(
        isOffline ? Icons.cloud_done_outlined : Icons.check_circle_outline_rounded,
        size: 80,
        color: color,
      ),
    );
  }

  Widget _buildReferenceCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 28),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.border),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            isOffline ? AppStrings.localIdLabel : AppStrings.incidentIdLabel,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppColors.textSecondary,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            incident.referenceId,
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w900,
              color: AppColors.primary,
              letterSpacing: 1.5,
            ),
          ),
          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 12),

          // Details row
          _DetailRow(
            icon: Icons.star_half_rounded,
            label: 'Severity Rating',
            value: '${incident.citizenRating} / 10',
            color: _ratingColor(incident.citizenRating),
          ),
          const SizedBox(height: 8),
          _DetailRow(
            icon: incident.hasLocation ? Icons.location_on_outlined : Icons.location_off_outlined,
            label: 'Location',
            value: incident.hasLocation
                ? '${incident.latitude!.toStringAsFixed(4)}, ${incident.longitude!.toStringAsFixed(4)}'
                : 'Unavailable',
            color: incident.hasLocation ? AppColors.success : AppColors.textSecondary,
          ),
          const SizedBox(height: 8),
          _DetailRow(
            icon: isOffline ? Icons.schedule_outlined : Icons.check_circle_outline,
            label: 'Status',
            value: isOffline ? AppStrings.statusWaitingToUpload : incident.statusLabel,
            color: isOffline ? AppColors.warning : AppColors.success,
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────
  // Phase 6: Risk Assessment Card
  // ─────────────────────────────────────────────────────────────────

  Widget _buildRiskAssessmentCard() {
    final riskColor = _riskLevelColor(incident.riskLevel ?? 'LOW');

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
      decoration: BoxDecoration(
        color: riskColor.withOpacity(0.06),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: riskColor.withOpacity(0.35), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: riskColor.withOpacity(0.10),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header row
          Row(
            children: [
              Icon(Icons.shield_outlined, size: 20, color: riskColor),
              const SizedBox(width: 8),
              const Text(
                'AI ASSESSMENT',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textSecondary,
                  letterSpacing: 1.4,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Risk score + level badge
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Score
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Risk Score',
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.textSecondary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${incident.riskScore!.toStringAsFixed(1)}/100',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w900,
                      color: riskColor,
                    ),
                  ),
                ],
              ),
              const Spacer(),
              // Risk level badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                decoration: BoxDecoration(
                  color: riskColor,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  incident.riskLevel ?? 'UNKNOWN',
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w800,
                    color: Colors.white,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 12),

          // Priority row
          _DetailRow(
            icon: Icons.priority_high_rounded,
            label: 'Priority',
            value: incident.priority ?? 'UNKNOWN',
            color: riskColor,
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────
  // Colour helpers
  // ─────────────────────────────────────────────────────────────────

  Color _ratingColor(int rating) {
    if (rating <= 3) return AppColors.success;
    if (rating <= 6) return AppColors.warning;
    if (rating <= 8) return const Color(0xFFEA580C);
    return AppColors.emergencyRed;
  }

  /// Returns a colour representing the risk level.
  Color _riskLevelColor(String level) {
    switch (level.toUpperCase()) {
      case 'CRITICAL':
        return AppColors.emergencyRed;
      case 'HIGH':
        return const Color(0xFFEA580C); // orange-red
      case 'MEDIUM':
        return AppColors.warning;      // amber
      case 'LOW':
      default:
        return AppColors.success;      // green
    }
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _DetailRow({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: color),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(
            fontSize: 13,
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: TextStyle(
            fontSize: 13,
            color: color,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}
