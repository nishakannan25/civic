/// Phase 2 — Incident Preview Screen.
///
/// Shows the captured image, the 0–10 severity slider, and a CONTINUE button.
/// On CONTINUE:
///   1. Captures GPS (with permission handling + timeout)
///   2. Shows loading state during upload
///   3. Submits to backend via IncidentRepository
///   4. Navigates to IncidentSuccessScreen on success
///   5. Shows user-friendly error on failure
///
/// Combined preview + rating in one screen (per spec §21).

import 'dart:io';
import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_strings.dart';
import '../../../core/network/api_client.dart';
import '../../../core/errors/exceptions.dart';
import '../data/incident_repository.dart';
import '../models/incident_model.dart';
import '../models/location_data.dart';
import '../services/location_service.dart';
import '../widgets/severity_slider.dart';
import 'incident_success_screen.dart';

class IncidentPreviewScreen extends StatefulWidget {
  final String imagePath;

  const IncidentPreviewScreen({super.key, required this.imagePath});

  @override
  State<IncidentPreviewScreen> createState() => _IncidentPreviewScreenState();
}

enum _SubmitState { idle, capturingGps, uploading }

class _IncidentPreviewScreenState extends State<IncidentPreviewScreen> {
  int _citizenRating = 5;
  _SubmitState _submitState = _SubmitState.idle;
  String _statusMessage = '';

  final _locationService = LocationService();

  // ── Submit Flow ──────────────────────────────────────────────────────────────

  Future<void> _submit() async {
    if (_submitState != _SubmitState.idle) return; // Prevent double-tap

    // Step 1 — Capture GPS
    setState(() {
      _submitState = _SubmitState.capturingGps;
      _statusMessage = AppStrings.capturingLocation;
    });

    final locationResult = await _locationService.captureLocation();

    if (!mounted) return;

    // Step 2 — Upload
    setState(() {
      _submitState = _SubmitState.uploading;
      _statusMessage = AppStrings.submitting;
    });

    // Build repository with the shared ApiClient.
    final apiClient = ApiClient();
    final token = _AuthStore.token;
    if (token != null) {
      apiClient.setAuthToken(token);
    }

    final repository = IncidentRepository(apiClient: apiClient);

    try {
      final localIncident = await repository.submitIncident(
        imagePath: widget.imagePath,
        citizenRating: _citizenRating,
        locationResult: locationResult,
      );

      if (!mounted) return;

      final incidentModel = IncidentModel(
        id: localIncident.serverId ?? 0,
        referenceId: localIncident.referenceId,
        userId: localIncident.userId,
        imageUrl: localIncident.imageUrl,
        latitude: localIncident.latitude,
        longitude: localIncident.longitude,
        gpsAccuracy: localIncident.gpsAccuracy,
        locationStatus: localIncident.locationStatus,
        timestamp: localIncident.timestamp,
        citizenRating: localIncident.citizenRating,
        status: localIncident.status,
        createdAt: localIncident.createdAt,
      );

      // Navigate to success screen with isOffline indicator
      await Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => IncidentSuccessScreen(
            incident: incidentModel,
            isOffline: !localIncident.isUploaded,
          ),
        ),
      );
    } on UploadException catch (e) {
      if (!mounted) return;
      setState(() => _submitState = _SubmitState.idle);
      _showError(_mapUploadError(e));
    } on NetworkException catch (_) {
      if (!mounted) return;
      setState(() => _submitState = _SubmitState.idle);
      _showError(AppStrings.submitFailureNetwork);
    } catch (_) {
      if (!mounted) return;
      setState(() => _submitState = _SubmitState.idle);
      _showError(AppStrings.submitFailureServer);
    }
  }

  String _mapUploadError(UploadException e) {
    final code = e.statusCode;
    if (code == 401 || code == 403) return AppStrings.submitFailureAuth;
    if (code == 408) return AppStrings.submitFailureTimeout;
    if (code != null && code >= 500) return AppStrings.submitFailureServer;
    return e.message.isNotEmpty ? e.message : AppStrings.submitFailureServer;
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(children: [
          const Icon(Icons.error_outline, color: Colors.white, size: 20),
          const SizedBox(width: 10),
          Expanded(child: Text(message)),
        ]),
        backgroundColor: AppColors.emergencyRed,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 5),
      ),
    );
  }

  void _retake() {
    Navigator.of(context).pop();
  }

  // ── Build ────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final isSubmitting = _submitState != _SubmitState.idle;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text(AppStrings.problemCaptured),
        leading: isSubmitting
            ? const SizedBox.shrink()
            : IconButton(
                icon: const Icon(Icons.arrow_back_ios_new),
                onPressed: _retake,
              ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // ── Image Preview ───────────────────────────────────────────
            Expanded(
              flex: 5,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      Image.file(
                        File(widget.imagePath),
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Container(
                          color: AppColors.cameraViewport,
                          child: const Center(
                            child: Text(
                              'Image preview unavailable',
                              style: TextStyle(color: Colors.white70),
                            ),
                          ),
                        ),
                      ),

                      // RETAKE button overlay
                      if (!isSubmitting)
                        Positioned(
                          top: 12,
                          right: 12,
                          child: Material(
                            color: Colors.black.withOpacity(0.55),
                            borderRadius: BorderRadius.circular(30),
                            child: InkWell(
                              borderRadius: BorderRadius.circular(30),
                              onTap: _retake,
                              child: const Padding(
                                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.replay, color: Colors.white, size: 18),
                                    SizedBox(width: 6),
                                    Text(
                                      AppStrings.retakePhoto,
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.w700,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),

            // ── Rating + Submit ────────────────────────────────────────
            Expanded(
              flex: 4,
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SeveritySlider(
                      value: _citizenRating,
                      onChanged: isSubmitting
                          ? (_) {}
                          : (v) => setState(() => _citizenRating = v),
                    ),

                    const SizedBox(height: 20),

                    // GPS status / upload status indicator
                    if (isSubmitting) ...[
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.primary.withOpacity(0.2)),
                        ),
                        child: Row(
                          children: [
                            const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2.5,
                                color: AppColors.primary,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                _statusMessage,
                                style: const TextStyle(
                                  color: AppColors.primary,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // SUBMIT button
                    SizedBox(
                      width: double.infinity,
                      height: 60,
                      child: ElevatedButton.icon(
                        onPressed: isSubmitting ? null : _submit,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          disabledBackgroundColor: AppColors.primary.withOpacity(0.5),
                          foregroundColor: Colors.white,
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        icon: isSubmitting
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.upload_rounded, size: 22),
                        label: Text(
                          isSubmitting ? _statusMessage : AppStrings.submitIncident,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.8,
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 16),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Simple in-memory token store for Phase 2.
///
/// Phase 3 will replace this with secure storage (flutter_secure_storage).
/// Use [_AuthStore.token] = token after login, and clear on logout.
class _AuthStore {
  static String? token;
}
