import 'package:flutter/material.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart' as mapbox;

class MapWidget extends StatefulWidget {
  final double latitude;
  final double longitude;

  const MapWidget({
    Key? key,
    required this.latitude,
    required this.longitude,
  }) : super(key: key);

  @override
  State<MapWidget> createState() => _MapWidgetState();
}

class _MapWidgetState extends State<MapWidget> {
  mapbox.MapboxMap? mapboxMap;

  _onMapCreated(mapbox.MapboxMap mapboxMap) async {
    this.mapboxMap = mapboxMap;
    
    // Add a red marker at the predicted location
    try {
      final pointAnnotationManager = await mapboxMap.annotations.createPointAnnotationManager();
      
      final options = <mapbox.PointAnnotationOptions>[
        mapbox.PointAnnotationOptions(
          geometry: mapbox.Point(
            coordinates: mapbox.Position(
              widget.longitude,
              widget.latitude,
            ),
          ),
          iconSize: 1.5,
          iconColor: Colors.red.value,
        ),
      ];
      
      await pointAnnotationManager.createMulti(options);
    } catch (e) {
      print('Error adding marker: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    // IMPORTANT: Replace with your PUBLIC Mapbox token (starts with pk.)
    const String MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiZmVsaXhncnVlbmVyIiwiYSI6ImNtYXR2dXIwaDB2YjEyanNod2duemdjMnoifQ._ZPv79B7Ud5CfUSdbBn3Ww';
    
    // Set the access token
    mapbox.MapboxOptions.setAccessToken(MAPBOX_ACCESS_TOKEN);
    
    return mapbox.MapWidget(
      key: const ValueKey("mapWidget"),
      mapOptions: mapbox.MapOptions(
        pixelRatio: MediaQuery.of(context).devicePixelRatio,
      ),
      cameraOptions: mapbox.CameraOptions(
        center: mapbox.Point(
          coordinates: mapbox.Position(
            widget.longitude,
            widget.latitude,
          ),
        ),
        zoom: 14.0,
      ),
      styleUri: mapbox.MapboxStyles.SATELLITE_STREETS,
      onMapCreated: _onMapCreated,
    );
  }
}