import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../data/offline_data.dart';

class StorageService {
  static const String _keyProfile = "air1_brother_profile";
  static const String _keyErrors = "air1_error_notebook";
  static const String _keyCbtAttempts = "air1_cbt_attempts";
  static const String _keySololearnProgress = "air1_sololearn_progress";
  static const String _keyBackendIp = "air1_backend_ip";

  static Future<Map<String, dynamic>> getProfile() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_keyProfile);
    if (raw != null) {
      try {
        return jsonDecode(raw) as Map<String, dynamic>;
      } catch (_) {}
    }
    return Map<String, dynamic>.from(OfflineData.defaultProfile);
  }

  static Future<void> saveProfile(Map<String, dynamic> profile) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyProfile, jsonEncode(profile));
  }

  static Future<List<Map<String, dynamic>>> getErrors() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_keyErrors);
    if (raw != null) {
      try {
        final list = jsonDecode(raw) as List;
        return list.map((e) => Map<String, dynamic>.from(e)).toList();
      } catch (_) {}
    }
    return []; // Zero fake data: Starts empty
  }

  static Future<void> addError(Map<String, dynamic> errorItem) async {
    final errors = await getErrors();
    errors.insert(0, errorItem);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyErrors, jsonEncode(errors));
  }

  static Future<List<Map<String, dynamic>>> getCbtAttempts() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_keyCbtAttempts);
    if (raw != null) {
      try {
        final list = jsonDecode(raw) as List;
        return list.map((e) => Map<String, dynamic>.from(e)).toList();
      } catch (_) {}
    }
    return []; // Zero fake data: Starts empty
  }

  static Future<void> recordCbtAttempt(Map<String, dynamic> attempt) async {
    final attempts = await getCbtAttempts();
    attempts.insert(0, attempt);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyCbtAttempts, jsonEncode(attempts));

    // Update profile metrics with real data
    final profile = await getProfile();
    profile["questions_solved"] = (profile["questions_solved"] as int? ?? 0) + (attempt["total_questions"] as int? ?? 0);
    int totalQuestions = profile["questions_solved"] as int;
    int correct = attempt["correct_count"] as int? ?? 0;
    if (totalQuestions > 0) {
      profile["overall_accuracy_pct"] = ((correct / totalQuestions) * 100).clamp(0, 100);
    }
    await saveProfile(profile);
  }

  static Future<Map<String, int>> getSoloLearnProgress() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_keySololearnProgress);
    if (raw != null) {
      try {
        final map = jsonDecode(raw) as Map<String, dynamic>;
        return map.map((k, v) => MapEntry(k, v as int));
      } catch (_) {}
    }
    return {};
  }

  static Future<void> updateSoloLearnStep(String moduleId, int stepIndex) async {
    final map = await getSoloLearnProgress();
    map[moduleId] = stepIndex;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keySololearnProgress, jsonEncode(map));
  }

  static Future<String> getBackendIp() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyBackendIp) ?? "10.0.2.2:8000";
  }

  static Future<void> saveBackendIp(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyBackendIp, ip);
  }
}
