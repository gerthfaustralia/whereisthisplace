import 'dart:convert';
import 'dart:io' show File, Platform;
import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:http/http.dart' as http;

import 'package:app/models/result_model.dart';
import 'package:app/models/engine.dart';

/* ---------- endpoint selection ---------- */
const _backendHost = String.fromEnvironment('BACKEND_HOST', defaultValue: '52.28.72.57');
const _androidEmulatorHost = '10.0.2.2';

final String _baseUrl = (() {
  final host = kDebugMode && Platform.isAndroid
      ? _androidEmulatorHost
      : _backendHost;
  return 'http://$host:8000';
})();

/* ---------- API service ---------- */
class Api {
  Api._();

  static Future<ResultModel> locate(File image, Engine engine) async {
    var uri = Uri.parse('$_baseUrl/predict');
    if (engine == Engine.openai) {
      uri = uri.replace(queryParameters: {'mode': 'openai'});
    }
    final req = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('photo', image.path));

    final streamed = await req.send();
    final resp = await http.Response.fromStream(streamed);

    if (resp.statusCode != 200) {
      throw Exception('API error ${resp.statusCode}: ${resp.body}');
    }
    return ResultModel.fromJson(jsonDecode(resp.body));
  }

  static Future<bool> isHealthy() async {
    try {
      final resp = await http.get(Uri.parse('$_baseUrl/health'));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
