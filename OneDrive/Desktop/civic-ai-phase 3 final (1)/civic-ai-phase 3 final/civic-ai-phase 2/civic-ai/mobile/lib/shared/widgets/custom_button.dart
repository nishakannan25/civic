import 'package:flutter/material.dart';

/// Reusable civic button with minimum 56px height for touch accessibility.
class CivicButton extends StatelessWidget {
  final String label;
  final IconData? icon;
  final VoidCallback onPressed;
  final Color backgroundColor;
  final Color foregroundColor;
  final bool isFullWidth;
  final double height;

  const CivicButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.backgroundColor = const Color(0xFF1E3A8A),
    this.foregroundColor = Colors.white,
    this.isFullWidth = true,
    this.height = 56.0,
  });

  @override
  Widget build(BuildContext context) {
    final buttonContent = Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (icon != null) ...[
          Icon(icon, size: 22, color: foregroundColor),
          const SizedBox(width: 10),
        ],
        Text(
          label,
          style: TextStyle(
            color: foregroundColor,
            fontSize: 16,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.8,
          ),
        ),
      ],
    );

    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      height: height,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: backgroundColor,
          foregroundColor: foregroundColor,
          elevation: 3,
          shadowColor: backgroundColor.withOpacity(0.4),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
        child: buttonContent,
      ),
    );
  }
}
