import 'dart:io';
import 'package:flutter/foundation.dart';

import '../models/result_model.dart';
import '../services/api.dart';
import '../models/engine.dart';

/// Notifier that performs the geolocation call and stores the last result.
class GeoProvider extends ChangeNotifier {
  final Future<ResultModel> Function(File, Engine) _locateFn;
  GeoProvider([Future<ResultModel> Function(File, Engine)? locateFn])
      : _locateFn = locateFn ?? Api.locate;

  ResultModel? _result;
  ResultModel? get result => _result;

  /// Upload [file] to the backend; notify listeners when done.
  Future<ResultModel> locate(File file, Engine engine) async {
    final res = await _locateFn(file, engine);
    _result = res;
    notifyListeners();
    return res;
  }
}
