import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:app/providers/settings_provider.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('defaults to false when no value stored', () async {
    final provider = SettingsProvider();
    await Future.delayed(Duration.zero);
    expect(provider.sendToLlm, isFalse);
  });

  test('toggle persists value', () async {
    var provider = SettingsProvider();
    await Future.delayed(Duration.zero);
    await provider.toggleSendToLlm(true);

    provider = SettingsProvider();
    await Future.delayed(Duration.zero);
    expect(provider.sendToLlm, isTrue);
  });
}
