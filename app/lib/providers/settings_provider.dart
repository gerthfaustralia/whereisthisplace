import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsProvider extends ChangeNotifier {
  static const _sendToLlmKey = 'send_to_llm';
  bool _sendToLlm = false;
  bool get sendToLlm => _sendToLlm;

  SettingsProvider() {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    _sendToLlm = prefs.getBool(_sendToLlmKey) ?? false;
    notifyListeners();
  }

  Future<void> toggleSendToLlm(bool value) async {
    _sendToLlm = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_sendToLlmKey, value);
    notifyListeners();
  }
}
