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
  String mapStyle = 'mapbox://styles/mapbox/streets-v12';

  _onMapCreated(mapbox.MapboxMap mapboxMap) async {
    this.mapboxMap = mapboxMap;
    
    // TEST: Use New York coordinates if 0,0 is passed
    final lat = widget.latitude == 0.0 ? 40.7128 : widget.latitude;
    final lng = widget.longitude == 0.0 ? -74.0060 : widget.longitude;
    
    print('Map created at coordinates: $lat, $lng');
    
    // Move camera to the actual location
    await mapboxMap.setCamera(mapbox.CameraOptions(
      center: mapbox.Point(
        coordinates: mapbox.Position(lng, lat),
      ),
      zoom: 12.0,
    ));
    
    // Add a red circle marker at the predicted location
    try {
      final circleAnnotationManager = await mapboxMap.annotations.createCircleAnnotationManager();
      
      final options = <mapbox.CircleAnnotationOptions>[
        mapbox.CircleAnnotationOptions(
          geometry: mapbox.Point(
            coordinates: mapbox.Position(lng, lat),
          ),
          circleColor: Colors.red.value,
          circleRadius: 10.0,
        ),
      ];
      
      await circleAnnotationManager.createMulti(options);
      print('Marker added successfully at $lat, $lng');
    } catch (e) {
      print('Error adding marker: $e');
    }
  }

  @override
  void initState() {
    super.initState();
    const String MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiZmVsaXhncnVlbmVyIiwiYSI6ImNtYXR2dXIwaDB2YjEyanNod2duemdjMnoifQ._ZPv79B7Ud5CfUSdbBn3Ww';
    mapbox.MapboxOptions.setAccessToken(MAPBOX_ACCESS_TOKEN);
    print('Mapbox token set');
  }

  @override
  Widget build(BuildContext context) {
    // TEST: Use New York coordinates if 0,0 is passed
    final lat = widget.latitude == 0.0 ? 40.7128 : widget.latitude;
    final lng = widget.longitude == 0.0 ? -74.0060 : widget.longitude;
    
    return Stack(
      children: [
        mapbox.MapWidget(
          key: ValueKey("mapWidget_$mapStyle"),
          cameraOptions: mapbox.CameraOptions(
            center: mapbox.Point(
              coordinates: mapbox.Position(lng, lat),
            ),
            zoom: 12.0,
          ),
          styleUri: mapStyle,
          onMapCreated: _onMapCreated,
          onStyleLoadedListener: (mapbox.StyleLoadedEventData event) {
            print('Style loaded: $mapStyle');
          },
        ),
        // Debug info
        Positioned(
          top: 10,
          left: 10,
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.9),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'Lat: ${lat.toStringAsFixed(4)}\nLng: ${lng.toStringAsFixed(4)}',
              style: const TextStyle(fontSize: 12),
            ),
          ),
        ),
        // Style buttons
        Positioned(
          top: 10,
          right: 10,
          child: Column(
            children: [
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    mapStyle = 'mapbox://styles/mapbox/streets-v12';
                  });
                },
                child: const Text('Street'),
              ),
              const SizedBox(height: 5),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    mapStyle = 'mapbox://styles/mapbox/satellite-v9';
                  });
                },
                child: const Text('Satellite'),
              ),
              const SizedBox(height: 5),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    mapStyle = 'mapbox://styles/mapbox/light-v11';
                  });
                },
                child: const Text('Light'),
              ),
            ],
          ),
        ),
      ],
    );
  }
}