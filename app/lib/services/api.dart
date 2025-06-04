import 'dart:convert';
import 'dart:io' show File, Platform;
import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart' as http_parser;

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
    
    // Debug logging
    print('🚀 API Request URL: $uri');
    print('🚀 Engine mode: ${engine.queryValue}');
    print('🚀 Image path: ${image.path}');
    print('🚀 Image exists: ${await image.exists()}');
    
    final req = http.MultipartRequest('POST', uri);
    
    try {
      // Explicitly set content type to ensure backend accepts it
      final multipartFile = await http.MultipartFile.fromPath(
        'photo', 
        image.path,
        contentType: http_parser.MediaType('image', 'jpeg'),
      );
      print('🚀 MultipartFile created: ${multipartFile.filename}, length: ${multipartFile.length}, contentType: ${multipartFile.contentType}');
      req.files.add(multipartFile);
    } catch (e) {
      print('❌ Error creating MultipartFile: $e');
      throw Exception('Failed to create multipart file: $e');
    }

    final streamed = await req.send();
    final resp = await http.Response.fromStream(streamed);
    
    // Debug response
    print('🚀 Response status: ${resp.statusCode}');
    print('🚀 Response body: ${resp.body}');

    if (resp.statusCode != 200) {
      throw Exception('API error ${resp.statusCode}: ${resp.body}');
    }
    
    try {
      final decodedJson = jsonDecode(resp.body);
      print('🚀 Decoded JSON: $decodedJson');
      return ResultModel.fromJson(decodedJson);
    } catch (e) {
      print('❌ JSON parsing error: $e');
      throw Exception('Failed to parse response: $e');
    }
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
