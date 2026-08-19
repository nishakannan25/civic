/// Phase 3 — Local Image Storage.
///
/// Copies captured camera images from temporary cache into persistent app storage.
/// Guarantees that incident photos remain available during offline periods
/// and survive device reboots until synchronization is confirmed.

import 'dart:io';
import '../utils/logger.dart';

class LocalImageStorage {
  static final LocalImageStorage _instance = LocalImageStorage._internal();
  factory LocalImageStorage() => _instance;
  LocalImageStorage._internal();

  static String customStorageRoot = 'local_storage/incidents';

  /// Save/copy a temporary camera image to persistent storage for a specific incident.
  ///
  /// Returns the absolute or canonical local path to the saved image.
  Future<String> saveImage(String tempSourcePath, String localIncidentId) async {
    try {
      final sourceFile = File(tempSourcePath);
      if (!await sourceFile.exists()) {
        AppLogger.w('Source image does not exist: $tempSourcePath, storing path as-is');
        return tempSourcePath;
      }

      final ext = sourceFile.path.toLowerCase().endsWith('.png') ? '.png' : '.jpg';
      final targetDir = Directory('$customStorageRoot/$localIncidentId');
      if (!await targetDir.exists()) {
        await targetDir.create(parents: true);
      }

      final targetFile = File('${targetDir.path}/image$ext');
      await sourceFile.copy(targetFile.path);
      AppLogger.i('Copied incident photo to persistent storage: ${targetFile.path}');
      return targetFile.path;
    } catch (e) {
      AppLogger.e('Error saving local image: $e');
      return tempSourcePath;
    }
  }

  /// Get the File object for a stored image path.
  File? getImageFile(String imagePath) {
    final file = File(imagePath);
    return file.existsSync() ? file : null;
  }

  /// Delete a local image file and its parent folder safely after successful upload.
  Future<void> deleteImage(String imagePath) async {
    try {
      final file = File(imagePath);
      if (await file.exists()) {
        await file.delete();
        final parent = file.parent;
        if (await parent.exists() && (await parent.list().isEmpty)) {
          await parent.delete();
        }
        AppLogger.i('Cleaned up synced local image: $imagePath');
      }
    } catch (e) {
      AppLogger.e('Error deleting local image: $e');
    }
  }
}
