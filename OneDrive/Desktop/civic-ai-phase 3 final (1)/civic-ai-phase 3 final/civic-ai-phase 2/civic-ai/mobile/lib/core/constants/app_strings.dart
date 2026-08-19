/// Phase 2 — Updated app_strings.dart with all Phase 2 UI strings.
class AppStrings {
  static const String appTitle = 'CIVIC AI';
  static const String appTagline = 'Intelligent Community Emergency & Civic Reporting';

  // ── Camera ──────────────────────────────────────────────────────────────────
  static const String captureProblem = 'CAPTURE PROBLEM';
  static const String cameraPlaceholder = '[ CAMERA PREVIEW ]';
  static const String cameraPlaceholderSubtitle = 'Phase 2 – Live Camera';
  static const String sosEmergency = '🚨 SOS';
  static const String sosSubtitle = 'Emergency Alert Dispatch';
  static const String retakePhoto = 'RETAKE';

  // Camera permissions / errors
  static const String cameraPermissionRequired =
      'Camera permission is required to report a civic problem.';
  static const String cameraPermissionDenied =
      'Camera access was denied. Please allow camera access to continue.';
  static const String cameraPermissionPermanentlyDenied =
      'Camera permission is permanently denied. Open Settings and enable Camera for Civic AI.';
  static const String cameraInitError =
      'Unable to start camera. Please try again.';
  static const String cameraCaptureError =
      'Could not capture image. Please try again.';
  static const String openSettings = 'Open Settings';
  static const String retry = 'Retry';
  static const String grantPermission = 'Grant Permission';

  // ── Rating ───────────────────────────────────────────────────────────────────
  static const String problemCaptured = 'Problem Captured';
  static const String ratingLabel = 'How serious is this problem for you?';
  static const String ratingHint = 'Move the slider to rate severity';
  static const String ratingMin = 'Minor';
  static const String ratingMax = 'Critical';
  static const String continueBtn = 'CONTINUE';

  // ── GPS ──────────────────────────────────────────────────────────────────────
  static const String capturingLocation = 'Capturing your location…';
  static const String locationCaptured = 'Location captured';
  static const String locationUnavailable = 'Location unavailable — continuing without GPS';
  static const String locationPermissionDenied =
      'Location permission denied. Your report will be submitted without GPS coordinates.';

  // ── Submission ───────────────────────────────────────────────────────────────
  static const String submitIncident = 'SUBMIT INCIDENT';
  static const String submitting = 'Submitting incident…';
  static const String submitSuccess = 'Incident reported successfully.';
  static const String submitFailureNetwork =
      'Unable to submit right now. Your report could not be uploaded. Check your internet connection.';
  static const String submitFailureServer =
      'Server error. Please try again later.';
  static const String submitFailureAuth =
      'Authentication failed. Please log in and try again.';
  static const String submitFailureTimeout =
      'Request timed out. Please check your connection and try again.';

  // ── Success screen ───────────────────────────────────────────────────────────
  static const String incidentSubmitted = 'Report Submitted!';
  static const String incidentSavedOffline = 'Report Saved on Device';
  static const String incidentSavedOfflineSubtitle =
      'Your report is saved on this device. It will be uploaded automatically when your connection returns.';
  static const String incidentIdLabel = 'Incident ID';
  static const String localIdLabel = 'Local Reference';
  static const String reportNewProblem = 'REPORT ANOTHER PROBLEM';
  static const String thankYouMessage =
      'Thank you for helping improve your community.';

  // ── Phase 3: Offline Sync & Statuses ─────────────────────────────────────────
  static const String statusWaitingToUpload = 'Waiting to upload';
  static const String statusUploading = 'Uploading';
  static const String statusUploaded = 'Uploaded';
  static const String statusNeedsAttention = 'Upload needs attention';
  static const String statusDraft = 'Draft';

  static const String savedReportsTitle = 'Saved Reports';
  static const String pendingSyncReports = 'Pending Sync';
  static const String syncNow = 'SYNC NOW';
  static const String syncing = 'Syncing...';
  static const String noSavedReports = 'No saved reports on this device.';
  static const String allReportsSynced = 'All reports have been successfully uploaded!';
  static const String syncCompleteNotification = 'Your saved report has been uploaded.';

  // ── SOS placeholder ──────────────────────────────────────────────────────────
  static const String sosPlaceholderMessage =
      'SOS functionality will be available in the emergency workflow.';

  // ── Navigation ───────────────────────────────────────────────────────────────
  static const String navCamera = 'Camera';
  static const String navIncidents = 'Incidents';
  static const String navSavedReports = 'Saved Reports';
  static const String navVerify = 'Verify';
  static const String navProfile = 'Profile';
  static const String navSettings = 'Settings';

  // ── Phase notices (Phase 4+) ─────────────────────────────────────────────────
  static const String phase4AI = 'Coming in Phase 4: AI Computer Vision & YOLO Classification';
  static const String phase5Verify = 'Coming in Phase 5: Community Verification Network';
  static const String phase6Profile = 'Coming in Phase 6: Citizen Trust & Reputation Profile';
}
