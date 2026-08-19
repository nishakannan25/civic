/// Phase 3 — Saved Reports & Sync Status Screen.
///
/// Clean, minimal view of local incident reports on this device.
/// Displays sync statuses (Waiting to upload, Uploading, Uploaded, Needs attention)
/// and provides a manual [ SYNC NOW ] trigger.

import 'dart:io';
import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_strings.dart';
import '../data/incident_repository.dart';
import '../models/local_incident.dart';
import '../services/sync_service.dart';

class PendingIncidentsScreen extends StatefulWidget {
  const PendingIncidentsScreen({super.key});

  @override
  State<PendingIncidentsScreen> createState() => _PendingIncidentsScreenState();
}

class _PendingIncidentsScreenState extends State<PendingIncidentsScreen> {
  final _repository = IncidentRepository();
  final _syncService = SyncService();
  List<LocalIncident> _incidents = [];
  bool _isLoading = true;
  bool _isSyncing = false;

  @override
  void initState() {
    super.initState();
    _loadIncidents();
    _syncService.isSyncingStream.listen((syncing) {
      if (mounted) {
        setState(() => _isSyncing = syncing);
        if (!syncing) _loadIncidents();
      }
    });
  }

  Future<void> _loadIncidents() async {
    setState(() => _isLoading = true);
    final list = await _repository.getAllLocalIncidents();
    if (mounted) {
      setState(() {
        _incidents = list;
        _isLoading = false;
      });
    }
  }

  Future<void> _triggerManualSync() async {
    if (_isSyncing) return;
    setState(() => _isSyncing = true);
    final count = await _syncService.syncPendingIncidents();
    if (mounted) {
      setState(() => _isSyncing = false);
      await _loadIncidents();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(count > 0
              ? 'Successfully uploaded $count report(s).'
              : 'No reports uploaded. Check internet connectivity.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  Future<void> _retrySingleIncident(String localId) async {
    await _repository.retryIncident(localId);
    await _syncService.syncPendingIncidents();
    await _loadIncidents();
  }

  @override
  Widget build(BuildContext context) {
    final pendingCount = _incidents.where((i) => i.isPending || i.isFailed).length;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text(AppStrings.savedReportsTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading || _isSyncing ? null : _loadIncidents,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // ── Top Summary & Manual Sync Bar ──────────────────────────────
            Container(
              padding: const EdgeInsets.all(16),
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.border),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.04),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '$pendingCount pending upload',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${_incidents.length} total report(s) on device',
                          style: const TextStyle(
                            fontSize: 13,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: _isSyncing || pendingCount == 0 ? null : _triggerManualSync,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      disabledBackgroundColor: AppColors.primary.withOpacity(0.3),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    icon: _isSyncing
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Icon(Icons.sync, size: 18),
                    label: Text(
                      _isSyncing ? AppStrings.syncing : AppStrings.syncNow,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ),
                ],
              ),
            ),

            // ── Incident List ──────────────────────────────────────────────
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _incidents.isEmpty
                      ? _buildEmptyState()
                      : ListView.separated(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          itemCount: _incidents.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 12),
                          itemBuilder: (context, index) {
                            final incident = _incidents[index];
                            return _buildIncidentCard(incident);
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.inbox_outlined, size: 64, color: AppColors.textSecondary.withOpacity(0.5)),
          const SizedBox(height: 16),
          const Text(
            AppStrings.noSavedReports,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIncidentCard(LocalIncident incident) {
    Color badgeColor;
    IconData badgeIcon;

    switch (incident.status) {
      case LocalIncidentStatus.uploaded:
        badgeColor = AppColors.success;
        badgeIcon = Icons.check_circle_outline;
        break;
      case LocalIncidentStatus.uploading:
        badgeColor = AppColors.primary;
        badgeIcon = Icons.sync;
        break;
      case LocalIncidentStatus.failed:
        badgeColor = AppColors.emergencyRed;
        badgeIcon = Icons.error_outline;
        break;
      case LocalIncidentStatus.pendingSync:
      default:
        badgeColor = AppColors.warning;
        badgeIcon = Icons.schedule;
        break;
    }

    final imageFile = File(incident.localImagePath);

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Thumbnail
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: SizedBox(
              width: 64,
              height: 64,
              child: imageFile.existsSync()
                  ? Image.file(imageFile, fit: BoxFit.cover)
                  : Container(
                      color: AppColors.cameraViewport,
                      child: const Icon(Icons.broken_image, color: Colors.white54),
                    ),
            ),
          ),
          const SizedBox(width: 14),

          // Details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        incident.referenceId,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                    // Status Badge
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: badgeColor.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(badgeIcon, size: 12, color: badgeColor),
                          const SizedBox(width: 4),
                          Text(
                            incident.statusLabel,
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: badgeColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  'Severity: ${incident.citizenRating}/10 • ${incident.locationStatus}',
                  style: const TextStyle(
                    fontSize: 13,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Created: ${_formatDate(incident.createdAt)}',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppColors.textSecondary.withOpacity(0.8),
                  ),
                ),

                // Error and retry for failed incidents
                if (incident.isFailed) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Expanded(
                        child: Text(
                          'Upload failed. Tap to retry.',
                          style: TextStyle(
                            fontSize: 11,
                            color: AppColors.emergencyRed,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      TextButton.icon(
                        onPressed: () => _retrySingleIncident(incident.localId),
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        icon: const Icon(Icons.refresh, size: 14),
                        label: const Text('Retry', style: TextStyle(fontSize: 12)),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime dt) {
    return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}
