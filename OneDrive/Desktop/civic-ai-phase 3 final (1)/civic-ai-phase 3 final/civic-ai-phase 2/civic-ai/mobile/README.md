# Civic AI - Mobile Application (Flutter)

Mobile client for the **Civic AI – Intelligent Community Emergency & Civic Problem Reporting System**.

## Package Details
- **Application Name**: Civic AI
- **Application ID / Namespace**: `com.civicai.app`
- **Framework**: Flutter (Dart)

## Phase 1 Scope & Features
- ✅ Modular, feature-first application architecture
- ✅ Accessible Civic & Emergency design system and theme
- ✅ Camera-first UI foundation screen with responsive viewfinder preview
- ✅ Large accessible touch targets (Capture Problem & 🚨 SOS)
- ✅ Bottom Navigation Shell for future modules
- ✅ Centralized API configuration supporting multi-environment development

## Running the Mobile App

### 1. Prerequisites
- Flutter SDK (>= 3.10.0)
- Android Studio / Xcode / Chrome for Web debugging

### 2. Configure Backend API URL
The backend API URL can be configured in `lib/core/config/app_config.dart` or via `--dart-define`:

```bash
# Android Emulator (default points to 10.0.2.2:8000)
flutter run

# iOS Simulator / macOS (points to 127.0.0.1:8000)
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000

# Physical Device (use your workstation's LAN IP)
flutter run --dart-define=API_BASE_URL=http://192.168.1.100:8000

# Flutter Web
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

### 3. Run Tests
```bash
flutter test
```
