/// Phase 2 — Severity Slider Widget (0–10 Citizen Rating).
///
/// Displays a styled slider with min/max labels and the current value.
/// Keeps the rating concept completely separate from AI severity.

import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_strings.dart';

class SeveritySlider extends StatelessWidget {
  final int value;
  final ValueChanged<int> onChanged;

  const SeveritySlider({
    super.key,
    required this.value,
    required this.onChanged,
  });

  Color get _thumbColor {
    if (value <= 3) return AppColors.success;
    if (value <= 6) return AppColors.warning;
    if (value <= 8) return const Color(0xFFEA580C); // orange
    return AppColors.emergencyRed;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label
        Text(
          AppStrings.ratingLabel,
          style: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w600,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 16),

        // Selected value badge
        Center(
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            decoration: BoxDecoration(
              color: _thumbColor,
              borderRadius: BorderRadius.circular(30),
              boxShadow: [
                BoxShadow(
                  color: _thumbColor.withOpacity(0.35),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Text(
              'Selected: $value / 10',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.5,
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Slider
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: _thumbColor,
            inactiveTrackColor: AppColors.border,
            thumbColor: _thumbColor,
            overlayColor: _thumbColor.withOpacity(0.18),
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 14),
            overlayShape: const RoundSliderOverlayShape(overlayRadius: 24),
            trackHeight: 6,
          ),
          child: Slider(
            value: value.toDouble(),
            min: 0,
            max: 10,
            divisions: 10,
            label: value.toString(),
            onChanged: (v) => onChanged(v.round()),
          ),
        ),

        // Min / Max labels
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 4),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                AppStrings.ratingMin,
                style: TextStyle(fontSize: 12, color: AppColors.success, fontWeight: FontWeight.w600),
              ),
              Text(
                AppStrings.ratingMax,
                style: TextStyle(fontSize: 12, color: AppColors.emergencyRed, fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
