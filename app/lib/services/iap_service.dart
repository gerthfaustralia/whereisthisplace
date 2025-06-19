import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:in_app_purchase/in_app_purchase.dart';

class IAPService {
  static const String productId = 'pro_monthly';
  static const String _kProductId = productId;
  
  final InAppPurchase _inAppPurchase = InAppPurchase.instance;
  late StreamSubscription<List<PurchaseDetails>> _subscription;
  
  // Available products
  List<ProductDetails> _products = [];
  List<ProductDetails> get products => _products;
  
  // Purchase stream controller
  final StreamController<PurchaseDetails> _purchaseController = 
      StreamController<PurchaseDetails>.broadcast();
  Stream<PurchaseDetails> get purchaseStream => _purchaseController.stream;
  
  // Error stream controller
  final StreamController<String> _errorController = 
      StreamController<String>.broadcast();
  Stream<String> get errorStream => _errorController.stream;
  
  bool _isAvailable = false;
  bool get isAvailable => _isAvailable;
  
  ProductDetails? get proProduct => 
      _products.where((p) => p.id == _kProductId).cast<ProductDetails?>().firstOrNull;

  IAPService() {
    // Initialize immediately - set up basic streams first
    _subscription = _inAppPurchase.purchaseStream.listen(
      _handlePurchaseUpdates,
      onDone: () => _subscription.cancel(),
      onError: (error) => _errorController.add('Purchase stream error: $error'),
    );
    
    // Initialize async operations
    initialize();
  }

  Future<void> initialize() async {
    try {
      // Check if IAP is available
      _isAvailable = await _inAppPurchase.isAvailable();
      
      if (!_isAvailable) {
        _errorController.add('In-app purchases are not available on this device.');
        return;
      }

      // Load products
      await loadProducts();
      
      // Restore previous purchases
      await restorePurchases();
    } catch (e) {
      _errorController.add('Failed to initialize IAP: $e');
    }
  }

  Future<void> loadProducts() async {
    if (!_isAvailable) return;
    
    // Skip product loading in debug mode to avoid store setup requirement
    if (kDebugMode) {
      debugPrint('🔧 DEBUG: Skipping IAP product loading - using debug mode');
      return;
    }
    
    try {
      const Set<String> productIds = {_kProductId};
      final ProductDetailsResponse response = 
          await _inAppPurchase.queryProductDetails(productIds);
      
      if (response.error != null) {
        _errorController.add('Error loading products: ${response.error!.message}');
        return;
      }
      
      _products = response.productDetails;
      
      if (_products.isEmpty) {
        _errorController.add('No products found. Make sure "$_kProductId" is configured in your app store.');
      }
    } catch (e) {
      _errorController.add('Exception loading products: $e');
    }
  }

  Future<void> buyProSubscription() async {
    // In debug mode, simulate purchase success without actual store interaction
    if (kDebugMode) {
      debugPrint('🔧 DEBUG: Simulating Pro subscription purchase');
      _handleDebugPurchaseSuccess();
      return;
    }
    
    if (!_isAvailable) {
      _errorController.add('In-app purchases are not available.');
      return;
    }
    
    final ProductDetails? product = proProduct;
    if (product == null) {
      _errorController.add('Pro monthly product not found.');
      return;
    }

    try {
      final PurchaseParam purchaseParam = PurchaseParam(productDetails: product);
      
      // Use different purchase methods for different platforms
      if (Platform.isAndroid) {
        await _inAppPurchase.buyNonConsumable(purchaseParam: purchaseParam);
      } else if (Platform.isIOS) {
        await _inAppPurchase.buyNonConsumable(purchaseParam: purchaseParam);
      } else {
        _errorController.add('Platform not supported for in-app purchases.');
      }
    } catch (e) {
      _errorController.add('Purchase failed: $e');
    }
  }

  Future<void> restorePurchases() async {
    if (!_isAvailable) return;
    
    try {
      await _inAppPurchase.restorePurchases();
    } catch (e) {
      _errorController.add('Restore purchases failed: $e');
    }
  }

  void _handlePurchaseUpdates(List<PurchaseDetails> purchaseDetailsList) {
    for (final PurchaseDetails purchaseDetails in purchaseDetailsList) {
      _handlePurchaseUpdate(purchaseDetails);
    }
  }

  void _handlePurchaseUpdate(PurchaseDetails purchaseDetails) {
    if (purchaseDetails.productID == _kProductId) {
      switch (purchaseDetails.status) {
        case PurchaseStatus.pending:
          // Handle pending purchase (e.g., show loading indicator)
          break;
        case PurchaseStatus.purchased:
        case PurchaseStatus.restored:
          // Handle successful purchase/restore
          _purchaseController.add(purchaseDetails);
          break;
        case PurchaseStatus.error:
          _errorController.add('Purchase error: ${purchaseDetails.error?.message ?? "Unknown error"}');
          break;
        case PurchaseStatus.canceled:
          _errorController.add('Purchase canceled by user.');
          break;
      }
    }

    // Complete the purchase for Android
    if (purchaseDetails.pendingCompletePurchase) {
      _inAppPurchase.completePurchase(purchaseDetails);
    }
  }

  void _handleDebugPurchaseSuccess() {
    if (kDebugMode) {
      // Create a mock successful purchase for debug mode
      final mockPurchase = _MockPurchaseDetails(
        productID: _kProductId,
        status: PurchaseStatus.purchased,
      );
      _purchaseController.add(mockPurchase);
    }
  }

  void dispose() {
    _subscription.cancel();
    _purchaseController.close();
    _errorController.close();
  }
}

// Mock purchase details for debug mode
class _MockPurchaseDetails extends PurchaseDetails {
  _MockPurchaseDetails({
    required String productID,
    required PurchaseStatus status,
  }) : super(
          purchaseID: 'debug_purchase_${DateTime.now().millisecondsSinceEpoch}',
          productID: productID,
          verificationData: PurchaseVerificationData(
            localVerificationData: 'debug_verification_data',
            serverVerificationData: 'debug_server_data',
            source: 'debug',
          ),
          transactionDate: DateTime.now().toIso8601String(),
          status: status,
        );

  @override
  bool get pendingCompletePurchase => false;

  @override
  IAPError? get error => null;
} 