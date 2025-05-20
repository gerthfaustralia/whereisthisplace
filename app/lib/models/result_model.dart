// Model class representing the API prediction result
class ResultModel {
  final double latitude;
  final double longitude;
  final double confidence;

  ResultModel({required this.latitude, required this.longitude, required this.confidence});

  factory ResultModel.fromJson(Map<String, dynamic> json) {
    return ResultModel(
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
    );
  }
}
