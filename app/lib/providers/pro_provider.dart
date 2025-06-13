import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ProProvider extends ChangeNotifier {
  static const _key = 'isPro';
  bool _isPro = false;
  bool get isPro => _isPro;

  ProProvider() {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    _isPro = prefs.getBool(_key) ?? false;
    notifyListeners();
  }

  Future<void> setPro(bool value) async {
    _isPro = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_key, value);
    notifyListeners();
  }
}
