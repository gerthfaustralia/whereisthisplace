import 'dart:io';
import 'package:flutter/foundation.dart';

import '../models/result_model.dart';
import '../services/api.dart';

/// Notifier that performs the geolocation call and stores the last result.
class GeoProvider extends ChangeNotifier {
  GeoProvider();

  ResultModel? _result;
  ResultModel? get result => _result;

  /// Upload [file] to the backend; notify listeners when done.
  Future<ResultModel> locate(File file) async {
    final res = await Api.locate(file);   // <-- static call
    _result = res;
    notifyListeners();
    return res;
  }
}
