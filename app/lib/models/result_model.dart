// Model class representing the API prediction result
class ResultModel {
  final double latitude;
  final double longitude;
  final double confidence;

  ResultModel({required this.latitude, required this.longitude, required this.confidence});

  factory ResultModel.fromJson(Map<String, dynamic> json) {
    // Handle the actual API response format: {status, filename, prediction: {lat, lon, score}, message}
    final prediction = json['prediction'] as Map<String, dynamic>;
    return ResultModel(
      latitude: (prediction['lat'] as num).toDouble(),
      longitude: (prediction['lon'] as num).toDouble(), 
      confidence: (prediction['score'] as num).toDouble(),
    );
  }
}
