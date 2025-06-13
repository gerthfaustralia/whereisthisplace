import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/iap_service.dart';

class ProProvider extends ChangeNotifier {
  static const _key = 'isPro';
  bool _isPro = false;
  bool get isPro => _isPro;

  late final IAPService _iapService;
  IAPService get iapService => _iapService;
  
  late StreamSubscription _purchaseSubscription;
  late StreamSubscription _errorSubscription;

  ProProvider() {
    _initializeIAP();
    _load();
  }

  void _initializeIAP() {
    _iapService = IAPService();
    
    // Listen to purchase events
    _purchaseSubscription = _iapService.purchaseStream.listen((purchase) {
      if (purchase.productID == 'pro_monthly') {
        setPro(true);
        if (kDebugMode) {
          print('✅ Pro subscription activated via IAP');
        }
      }
    });
    
    // Listen to error events
    _errorSubscription = _iapService.errorStream.listen((error) {
      if (kDebugMode) {
        print('❌ IAP Error: $error');
      }
      // You could emit these errors to UI via a separate stream or callback
    });
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    _isPro = prefs.getBool(_key) ?? false;
    notifyListeners();
  }

  Future<void> setPro(bool value) async {
    _isPro = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_key, value);
    notifyListeners();
  }
  
  Future<void> buyProSubscription() async {
    await _iapService.buyProSubscription();
  }
  
  Future<void> restorePurchases() async {
    await _iapService.restorePurchases();
  }
  
  bool get hasProProduct => _iapService.proProduct != null;
  
  String get proProductPrice => _iapService.proProduct?.price ?? 'CHF 5.99';

  @override
  void dispose() {
    _purchaseSubscription.cancel();
    _errorSubscription.cancel();
    _iapService.dispose();
    super.dispose();
  }
}
