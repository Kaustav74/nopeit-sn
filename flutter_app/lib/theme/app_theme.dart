import 'package:flutter/material.dart';

class AppTheme {
  // Brand Colors matching the web UI
  static const Color background = Color(0xFF070B14);
  static const Color surface = Color(0xFF0F172A);
  static const Color card = Color(0xFF1E293B);
  static const Color cardBorder = Color(0xFF334155);
  
  static const Color gold = Color(0xFFF59E0B);
  static const Color goldLight = Color(0xFFFBBF24);
  static const Color cyan = Color(0xFF06B6D4);
  static const Color cyanLight = Color(0xFF38BDF8);
  static const Color indigo = Color(0xFF6366F1);
  static const Color emerald = Color(0xFF10B981);
  static const Color rose = Color(0xFFEF4444);
  static const Color purple = Color(0xFF8B5CF6);

  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      primaryColor: gold,
      colorScheme: const ColorScheme.dark(
        primary: gold,
        secondary: cyan,
        surface: surface,
        error: rose,
        onPrimary: Colors.black,
        onSecondary: Colors.black,
        onSurface: textPrimary,
      ),
      cardTheme: CardTheme(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: cardBorder, width: 1),
          borderRadius: BorderRadius.circular(16),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: surface,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.5,
        ),
        iconTheme: IconThemeData(color: textPrimary),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surface,
        selectedItemColor: gold,
        unselectedItemColor: textMuted,
        type: BottomNavigationBarType.fixed,
        selectedLabelStyle: TextStyle(fontWeight: FontWeight.w700, fontSize: 11),
        unselectedLabelStyle: TextStyle(fontWeight: FontWeight.w500, fontSize: 10),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: gold,
          foregroundColor: Colors.black,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 14,
            letterSpacing: 0.5,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPrimary,
          side: const BorderSide(color: cardBorder),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 13,
          ),
        ),
      ),
    );
  }
}
