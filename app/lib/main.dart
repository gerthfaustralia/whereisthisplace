import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/geo_provider.dart';
import 'screens/home_screen.dart';      // ← this is already in the repo

void main() => runApp(const WhereApp());

class WhereApp extends StatelessWidget {
  const WhereApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => GeoProvider()),
      ],
      child: MaterialApp(
        title: 'AI Photo Geolocation',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          useMaterial3: true,
        ),
        home: const HomeScreen(),
      ),
    );
  }
}
