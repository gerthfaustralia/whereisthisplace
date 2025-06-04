import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/engine.dart';

class SettingsProvider extends ChangeNotifier {
  static const _engineKey = 'engine';
  Engine _engine = Engine.defaultEngine;
  Engine get engine => _engine;

  SettingsProvider() {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(_engineKey);
    _engine = stored == 'openai' ? Engine.openai : Engine.defaultEngine;
    notifyListeners();
  }

  Future<void> setEngine(Engine value) async {
    _engine = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_engineKey, value.queryValue);
    notifyListeners();
  }
}
