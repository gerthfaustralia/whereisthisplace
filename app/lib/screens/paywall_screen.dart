import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:flutter/material.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:provider/provider.dart';

import '../providers/pro_provider.dart';

const _kProduct = 'pro_monthly';

class PaywallScreen extends StatefulWidget {
  const PaywallScreen({super.key});

  @override
  State<PaywallScreen> createState() => _PaywallScreenState();
}

class _PaywallScreenState extends State<PaywallScreen> {
  ProductDetails? _product;
  late final Stream<List<PurchaseDetails>> _stream;

  @override
  void initState() {
    super.initState();
    _stream = InAppPurchase.instance.purchaseStream;
    _loadProduct();
    _stream.listen(_listenToPurchases);
  }

  Future<void> _loadProduct() async {
    final available = await InAppPurchase.instance.isAvailable();
    if (!available) return;
    final response = await InAppPurchase.instance.queryProductDetails({_kProduct});
    if (response.error == null && response.productDetails.isNotEmpty) {
      setState(() {
        _product = response.productDetails.first;
      });
    }
  }

  void _listenToPurchases(List<PurchaseDetails> purchases) {
    for (var p in purchases) {
      if (p.productID == _kProduct && p.status == PurchaseStatus.purchased) {
        context.read<ProProvider>().setPro(true);
      }
    }
  }

  void _buy() {
    final product = _product;
    if (product == null) return;
    final purchaseParam = PurchaseParam(productDetails: product);
    if (Theme.of(context).platform == TargetPlatform.android) {
      InAppPurchase.instance.buyNonConsumable(purchaseParam: purchaseParam);
    } else {
      InAppPurchase.instance.buy(purchaseParam: purchaseParam);
    }

    if (kDebugMode) {
      // Stub purchase success in debug builds
      context.read<ProProvider>().setPro(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Unlock Pro')),
      body: Center(
        child: _product == null
            ? const CircularProgressIndicator()
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(_product!.title, style: Theme.of(context).textTheme.headlineSmall),
                  const SizedBox(height: 8),
                  Text(_product!.price),
                  const SizedBox(height: 16),
                  ElevatedButton(onPressed: _buy, child: const Text('Buy')),
                ],
              ),
      ),
    );
  }
}
