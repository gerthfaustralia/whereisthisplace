import 'package:flutter/widgets.dart';

class AppLocalizations {
  final Locale locale;
  AppLocalizations(this.locale);

  static const localizedValues = <String, Map<String, String>>{
    'en': {
      'home': 'Home',
      'result': 'Result',
      'settings': 'Settings',
      'privacy_policy': 'Privacy Policy',
    },
    'de': {
      'home': 'Startseite',
      'result': 'Ergebnis',
      'settings': 'Einstellungen',
      'privacy_policy': 'Datenschutzerklärung',
    },
  };

  static const supportedLocales = [Locale('en'), Locale('de')];

  String get home => localizedValues[locale.languageCode]!['home']!;
  String get result => localizedValues[locale.languageCode]!['result']!;
  String get settings => localizedValues[locale.languageCode]!['settings']!;
  String get privacyPolicy =>
      localizedValues[locale.languageCode]!['privacy_policy']!;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }
}

class AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) =>
      AppLocalizations.localizedValues.keys.contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async => AppLocalizations(locale);

  @override
  bool shouldReload(AppLocalizationsDelegate old) => false;
}
