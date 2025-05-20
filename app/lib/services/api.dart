// API service for WhereIsThisPlace Flutter app

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';

import '../models/result_model.dart';

class Api {
  final HttpClient _client = HttpClient();

  String get _baseUrl {
    if (!kIsWeb && Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }

  /// Uploads [file] to the prediction endpoint and returns the location result.
  Future<ResultModel> locate(File file) async {
    final uri = Uri.parse('$_baseUrl/predict');
    final request = await _client.postUrl(uri);

    final boundary = '----dart-http-boundary-${DateTime.now().millisecondsSinceEpoch}';
    request.headers.contentType =
        ContentType('multipart', 'form-data', parameters: {'boundary': boundary});

    // Build multipart body
    final fileBytes = await file.readAsBytes();
    final filename = file.path.split(Platform.pathSeparator).last;
    final header =
        '--$boundary\r\nContent-Disposition: form-data; name="photo"; filename="$filename"\r\nContent-Type: application/octet-stream\r\n\r\n';
    final footer = '\r\n--$boundary--\r\n';

    request.contentLength =
        header.length + fileBytes.length + footer.length;

    request.write(header);
    request.add(fileBytes);
    request.write(footer);

    final response = await request.close();
    final body = await response.transform(utf8.decoder).join();
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return ResultModel.fromJson(jsonDecode(body) as Map<String, dynamic>);
    }
    throw HttpException('Failed to locate: ${response.statusCode} $body');
  }
}
