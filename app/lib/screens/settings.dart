import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/settings_provider.dart';
import '../providers/locale_provider.dart';
import '../l10n/app_localizations.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final settings = context.watch<SettingsProvider>();
    final localeProvider = context.watch<LocaleProvider>();
    return Scaffold(
      appBar: AppBar(title: Text(AppLocalizations.of(context).settings)),
      body: ListView(
        children: [
          SwitchListTile(
            key: const Key('send_to_llm_toggle'),
            title: const Text('Send to OpenAI LLM'),
            value: settings.sendToLlm,
            onChanged: settings.toggleSendToLlm,
          ),
          ListTile(
            title: DropdownButton<Locale>(
              key: const Key('locale_dropdown'),
              value: localeProvider.locale,
              items: const [
                DropdownMenuItem(value: Locale('en'), child: Text('English')),
                DropdownMenuItem(value: Locale('de'), child: Text('Deutsch')),
              ],
              onChanged: (locale) {
                if (locale != null) localeProvider.setLocale(locale);
              },
            ),
          ),
        ],
      ),
    );
  }
}
