import 'dart:convert';
import 'dart:io' show File, Platform;
import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart' as http_parser;

import 'package:app/models/result_model.dart';
import 'package:app/models/engine.dart';

/* ---------- endpoint selection ---------- */
const _backendHost = String.fromEnvironment('BACKEND_HOST', defaultValue: 'dualstack.bbalancer-1902268736.eu-central-1.elb.amazonaws.com');
const _androidEmulatorHost = '10.0.2.2';

final String _baseUrl = (() {
  // Use emulator host only for actual Android emulator, not real devices
  if (kDebugMode && Platform.isAndroid) {
    // Check if running on emulator vs real device
    // For emulator: use 10.0.2.2:8000
    // For real device: use load balancer on port 80
    return 'http://$_backendHost';
  }
  
  // Production: use load balancer on port 80 (forwards to EC2:8000)
  return 'http://$_backendHost';
})();

/* ---------- API service ---------- */
class Api {
  Api._();

  static Future<ResultModel> locate(File image, Engine engine) async {
    return _locateWithRetry(image, engine, maxRetries: 3);
  }

  static Future<ResultModel> _locateWithRetry(File image, Engine engine, {int maxRetries = 3}) async {
    var uri = Uri.parse('$_baseUrl/predict');
    if (engine == Engine.openai) {
      uri = uri.replace(queryParameters: {'mode': 'openai'});
    }
    
    Exception? lastException;
    
    for (int attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // Debug logging
        if (attempt > 0) {
          print('🔄 Retry attempt $attempt/$maxRetries');
        }
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

        if (resp.statusCode == 200) {
          try {
            final decodedJson = jsonDecode(resp.body);
            print('🚀 Decoded JSON: $decodedJson');
            return ResultModel.fromJson(decodedJson);
          } catch (e) {
            print('❌ JSON parsing error: $e');
            throw Exception('Failed to parse response: $e');
          }
        } else if (resp.statusCode == 429) {
          // Rate limiting - specific handling
          print('⚠️ Rate limit hit (429), attempt $attempt/$maxRetries');
          
          if (attempt == maxRetries) {
            throw Exception('Service is temporarily busy due to high traffic. Please try again in a few minutes.');
          }
          
          // Exponential backoff: 2^attempt seconds (2s, 4s, 8s)
          final delaySeconds = (2 << attempt);
          print('⏳ Waiting ${delaySeconds}s before retry...');
          await Future.delayed(Duration(seconds: delaySeconds));
          continue;
          
        } else if (resp.statusCode >= 500) {
          // Server error - retry
          print('🔴 Server error (${resp.statusCode}), attempt $attempt/$maxRetries');
          
          if (attempt == maxRetries) {
            throw Exception('Server error. Please try again later.');
          }
          
          // Shorter delay for server errors
          final delaySeconds = attempt + 1;
          print('⏳ Waiting ${delaySeconds}s before retry...');
          await Future.delayed(Duration(seconds: delaySeconds));
          continue;
          
        } else {
          // Other client errors - don't retry
          String errorMessage;
          switch (resp.statusCode) {
            case 400:
              errorMessage = 'Invalid image format. Please try a different photo.';
              break;
            case 413:
              errorMessage = 'Image file is too large. Please try a smaller image.';
              break;
            case 503:
              errorMessage = 'Service temporarily unavailable. Please try again later.';
              break;
            default:
              errorMessage = 'Request failed (${resp.statusCode}). Please try again.';
          }
          throw Exception(errorMessage);
        }
        
      } catch (e) {
        lastException = e is Exception ? e : Exception(e.toString());
        
        // Don't retry for non-network errors
        if (e.toString().contains('Failed to create multipart file') ||
            e.toString().contains('Failed to parse response')) {
          throw lastException;
        }
        
        // Network/timeout errors - retry
        if (attempt < maxRetries) {
          print('❌ Network error, retrying: $e');
          await Future.delayed(Duration(seconds: attempt + 1));
          continue;
        }
      }
    }
    
    // All retries exhausted
    throw lastException ?? Exception('Failed to get location after $maxRetries attempts');
  }

  static Future<bool> isHealthy() async {
    try {
      final resp = await http.get(
        Uri.parse('$_baseUrl/health'),
        headers: {'Accept': 'application/json'},
      ).timeout(Duration(seconds: 10));
      
      // Consider 429 as "healthy but busy" rather than unhealthy
      return resp.statusCode == 200 || resp.statusCode == 429;
    } catch (_) {
      return false;
    }
  }
}
