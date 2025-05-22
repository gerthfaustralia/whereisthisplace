import 'dart:io';
import 'package:flutter/foundation.dart';

import '../models/result_model.dart';
import '../services/api.dart';

/// ChangeNotifier that performs geolocation requests and stores the last result.
class GeoProvider extends ChangeNotifier {
  final Api api;

  GeoProvider(this.api);

  ResultModel? _result;
  ResultModel? get result => _result;

  /// Calls the API to locate the image in [file] and stores the returned result.
  /// The result is also returned for convenience.
  Future<ResultModel> locate(File file) async {
    final res = await api.locate(file);
    _result = res;
    notifyListeners();
    return res;
  }
}
