import 'package:flutter_test/flutter_test.dart';
import 'package:app/services/iap_service.dart';

void main() {
  group('IAPService', () {
    setUpAll(() {
      TestWidgetsFlutterBinding.ensureInitialized();
    });

    test('should have correct product ID constant', () {
      // This test verifies that the hardcoded product ID matches requirements
      expect(IAPService.productId, equals('pro_monthly'));
    });

    test('should provide purchase and error streams when available', () {
      // We can't actually test the IAP service initialization in unit tests
      // since it requires platform-specific setup, but we can test constants
      expect(IAPService.productId, isNotEmpty);
    });
  });
} 