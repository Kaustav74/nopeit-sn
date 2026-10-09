import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'theme/app_theme.dart';
import 'screens/home_navigation.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: AppTheme.surface,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );
  runApp(const JeeAir1App());
}

class JeeAir1App extends StatelessWidget {
  const JeeAir1App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JEE AIR-1 Companion',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const HomeNavigation(),
    );
  }
}
