/// Phase 2 — Camera-First Screen with live camera preview.
///
/// Replaces the Phase 1 placeholder with a real camera using the `camera` plugin.
/// Handles:
///   A. Camera permission (granted / denied / permanently denied)
///   B. Camera initialisation
///   C. Live camera preview
///   D. Image capture
///   E. Navigation to IncidentPreviewScreen on capture
///   F. SOS placeholder (Phase 2)

import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_strings.dart';
import '../widgets/camera_permission_view.dart';
import 'incident_preview_screen.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

enum _CameraState {
  requesting,   // Checking/requesting permission
  denied,       // Soft-denied — can re-request
  permanentlyDenied, // Hard-denied — must go to Settings
  initialising, // Permission granted, camera starting
  ready,        // Camera live and ready to capture
  error,        // Camera init failed
  capturing,    // Shutter pressed, capture in flight
}

class _CameraScreenState extends State<CameraScreen> with WidgetsBindingObserver {
  CameraController? _controller;
  _CameraState _state = _CameraState.requesting;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _checkPermissionAndInit();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller?.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // Re-initialise camera when app comes back to foreground (e.g. after Settings)
    if (state == AppLifecycleState.resumed) {
      _checkPermissionAndInit();
    } else if (state == AppLifecycleState.inactive) {
      _controller?.dispose();
    }
  }

  // ── Permission + Initialisation ──────────────────────────────────────────────

  Future<void> _checkPermissionAndInit() async {
    setState(() => _state = _CameraState.requesting);

    final status = await Permission.camera.status;

    if (status.isGranted) {
      await _initCamera();
      return;
    }

    if (status.isPermanentlyDenied) {
      setState(() => _state = _CameraState.permanentlyDenied);
      return;
    }

    // Request permission
    final result = await Permission.camera.request();

    if (result.isGranted) {
      await _initCamera();
    } else if (result.isPermanentlyDenied) {
      setState(() => _state = _CameraState.permanentlyDenied);
    } else {
      setState(() => _state = _CameraState.denied);
    }
  }

  Future<void> _initCamera() async {
    setState(() => _state = _CameraState.initialising);

    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        setState(() {
          _state = _CameraState.error;
          _errorMessage = AppStrings.cameraInitError;
        });
        return;
      }

      // Prefer the back camera for civic reporting
      final camera = cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      final controller = CameraController(
        camera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );

      await controller.initialize();

      if (!mounted) return;

      setState(() {
        _controller = controller;
        _state = _CameraState.ready;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _state = _CameraState.error;
        _errorMessage = AppStrings.cameraInitError;
      });
    }
  }

  // ── Capture ──────────────────────────────────────────────────────────────────

  Future<void> _captureImage() async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) return;
    if (_state == _CameraState.capturing) return; // Prevent double-tap

    setState(() => _state = _CameraState.capturing);

    try {
      final file = await controller.takePicture();

      if (!mounted) return;

      // Navigate to preview+rating screen
      await Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => IncidentPreviewScreen(imagePath: file.path),
        ),
      );

      // Restore state when returning from preview
      if (mounted) setState(() => _state = _CameraState.ready);
    } catch (e) {
      if (!mounted) return;
      setState(() => _state = _CameraState.ready);
      _showError(AppStrings.cameraCaptureError);
    }
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
        duration: const Duration(seconds: 4),
      ),
    );
  }

  void _showSosPlaceholder() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(AppStrings.sosPlaceholderMessage),
        duration: Duration(seconds: 4),
      ),
    );
  }

  // ── Build ────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    switch (_state) {
      case _CameraState.requesting:
      case _CameraState.initialising:
        return _buildLoading();

      case _CameraState.denied:
        return CameraPermissionView(
          isPermanentlyDenied: false,
          onRetry: _checkPermissionAndInit,
        );

      case _CameraState.permanentlyDenied:
        return CameraPermissionView(
          isPermanentlyDenied: true,
          onRetry: _checkPermissionAndInit,
        );

      case _CameraState.error:
        return _buildError();

      case _CameraState.ready:
      case _CameraState.capturing:
        return _buildCameraView();
    }
  }

  Widget _buildLoading() {
    return Scaffold(
      backgroundColor: AppColors.cameraViewport,
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: AppColors.primaryLight),
            SizedBox(height: 20),
            Text(
              'Starting camera…',
              style: TextStyle(color: Colors.white70, fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildError() {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text(AppStrings.appTitle)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.videocam_off_outlined, size: 64, color: AppColors.textSecondary),
              const SizedBox(height: 24),
              Text(
                _errorMessage.isNotEmpty ? _errorMessage : AppStrings.cameraInitError,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 16, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: _initCamera,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  icon: const Icon(Icons.refresh),
                  label: const Text(AppStrings.retry,
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCameraView() {
    final controller = _controller!;
    final isCapturing = _state == _CameraState.capturing;

    return Scaffold(
      backgroundColor: AppColors.cameraViewport,
      appBar: AppBar(
        backgroundColor: AppColors.cameraViewport,
        foregroundColor: Colors.white,
        centerTitle: true,
        elevation: 0,
        title: const Text(
          AppStrings.appTitle,
          style: TextStyle(
            fontWeight: FontWeight.w800,
            fontSize: 20,
            letterSpacing: 1.5,
            color: Colors.white,
          ),
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.success.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.success.withOpacity(0.4)),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.fiber_manual_record, size: 10, color: AppColors.success),
                SizedBox(width: 4),
                Text('LIVE', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppColors.success)),
              ],
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // ── Camera Preview ──────────────────────────────────────────────
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(20),
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      // Live preview
                      CameraPreview(controller),

                      // Viewfinder corner brackets
                      _ViewfinderOverlay(),

                      // Dimming during capture
                      if (isCapturing)
                        const ColoredBox(
                          color: Color(0x88000000),
                          child: Center(
                            child: CircularProgressIndicator(color: Colors.white),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 20),

            // ── CAPTURE PROBLEM Button ────────────────────────────────────
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: SizedBox(
                width: double.infinity,
                height: 60,
                child: ElevatedButton.icon(
                  onPressed: isCapturing ? null : _captureImage,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    disabledBackgroundColor: AppColors.primary.withOpacity(0.5),
                    foregroundColor: Colors.white,
                    elevation: 4,
                    shadowColor: AppColors.primary.withOpacity(0.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  icon: const Icon(Icons.camera, size: 24),
                  label: const Text(
                    AppStrings.captureProblem,
                    style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, letterSpacing: 1),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 12),

            // ── SOS Button ────────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: SizedBox(
                width: double.infinity,
                height: 56,
                child: OutlinedButton.icon(
                  onPressed: _showSosPlaceholder,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppColors.emergencyRed,
                    side: const BorderSide(color: AppColors.emergencyRed, width: 2),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  icon: const Text('🚨', style: TextStyle(fontSize: 18)),
                  label: const Text(
                    'SOS',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, letterSpacing: 1),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

/// Viewfinder corner bracket overlay for the camera preview.
class _ViewfinderOverlay extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: CustomPaint(
        painter: _CornerBracketPainter(),
      ),
    );
  }
}

class _CornerBracketPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.7)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    const margin = 24.0;
    const len = 30.0;

    // Top-left
    canvas.drawLine(Offset(margin, margin + len), Offset(margin, margin), paint);
    canvas.drawLine(Offset(margin, margin), Offset(margin + len, margin), paint);
    // Top-right
    canvas.drawLine(Offset(size.width - margin - len, margin), Offset(size.width - margin, margin), paint);
    canvas.drawLine(Offset(size.width - margin, margin), Offset(size.width - margin, margin + len), paint);
    // Bottom-left
    canvas.drawLine(Offset(margin, size.height - margin - len), Offset(margin, size.height - margin), paint);
    canvas.drawLine(Offset(margin, size.height - margin), Offset(margin + len, size.height - margin), paint);
    // Bottom-right
    canvas.drawLine(Offset(size.width - margin - len, size.height - margin), Offset(size.width - margin, size.height - margin), paint);
    canvas.drawLine(Offset(size.width - margin, size.height - margin), Offset(size.width - margin, size.height - margin - len), paint);
  }

  @override
  bool shouldRepaint(_CornerBracketPainter oldDelegate) => false;
}
