import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:app/providers/geo_provider.dart';
import 'package:app/models/engine.dart';
import 'package:app/models/result_model.dart';

void main() {
  test('locate stores result and notifies listeners', () async {
    final provider = GeoProvider(_fakeLocate);
    var notified = false;
    provider.addListener(() => notified = true);
    final result = await provider.locate(File('dummy'), Engine.defaultEngine);
    expect(notified, isTrue);
    expect(result.latitude, 1);
    expect(provider.result, isNotNull);
    expect(provider.result!.latitude, 1);
  });
}

Future<ResultModel> _fakeLocate(File file, Engine engine) async {
  return ResultModel(latitude: 1, longitude: 2, confidence: 0.5);
}
