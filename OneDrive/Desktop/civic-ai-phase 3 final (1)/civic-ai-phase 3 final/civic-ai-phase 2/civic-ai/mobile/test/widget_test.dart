import 'package:flutter_test/flutter_test.dart';
import 'package:civic_ai/app/app.dart';
import 'package:civic_ai/core/constants/app_strings.dart';

void main() {
  testWidgets('Civic AI initial camera-first screen renders correctly', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const CivicAiApp());

    // Verify that AppBar title is rendered
    expect(find.text(AppStrings.appTitle), findsOneWidget);

    // Verify that Camera Preview placeholder is displayed
    expect(find.text(AppStrings.cameraPlaceholder), findsOneWidget);

    // Verify that CAPTURE PROBLEM button is displayed
    expect(find.text(AppStrings.captureProblem), findsOneWidget);

    // Verify that SOS button is displayed
    expect(find.text(AppStrings.sosEmergency), findsOneWidget);

    // Tap the Capture Problem button and verify the Phase 2 SnackBar notice appears
    await tester.tap(find.text(AppStrings.captureProblem));
    await tester.pump();

    expect(find.text(AppStrings.phase2Camera), findsOneWidget);
  });
}
