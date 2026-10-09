import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/storage_service.dart';
import '../data/offline_data.dart';

class ProfileCockpitScreen extends StatefulWidget {
  const ProfileCockpitScreen({super.key});

  @override
  State<ProfileCockpitScreen> createState() => _ProfileCockpitScreenState();
}

class _ProfileCockpitScreenState extends State<ProfileCockpitScreen> {
  Map<String, dynamic> _profile = OfflineData.defaultProfile;
  String _backendIp = "10.0.2.2:8000";
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    final p = await StorageService.getProfile();
    final ip = await StorageService.getBackendIp();
    if (mounted) {
      setState(() {
        _profile = p;
        _backendIp = ip;
        _loading = false;
      });
    }
  }

  void _showEditProfileDialog() {
    final nameCtrl = TextEditingController(text: _profile["student_name"]);
    final goalCtrl = TextEditingController(text: _profile["primary_goal"]);
    final collegeCtrl = TextEditingController(text: _profile["target_college"]);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.surface,
        title: const Text("Edit Brother's Profile", style: TextStyle(color: AppTheme.gold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(labelText: "Student Name", labelStyle: TextStyle(color: AppTheme.textMuted)),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: goalCtrl,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(labelText: "Primary Goal", labelStyle: TextStyle(color: AppTheme.textMuted)),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: collegeCtrl,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(labelText: "Target College", labelStyle: TextStyle(color: AppTheme.textMuted)),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("CANCEL", style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            onPressed: () async {
              final nav = Navigator.of(ctx);
              setState(() {
                _profile["student_name"] = nameCtrl.text.trim();
                _profile["primary_goal"] = goalCtrl.text.trim();
                _profile["target_college"] = collegeCtrl.text.trim();
              });
              await StorageService.saveProfile(_profile);
              if (mounted) nav.pop();
            },
            child: const Text("SAVE PROFILE"),
          )
        ],
      ),
    );
  }

  void _showIpConfigDialog() {
    final ipCtrl = TextEditingController(text: _backendIp);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.surface,
        title: const Text("Local Server Sync Configuration", style: TextStyle(color: AppTheme.cyan)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "The app is 100% self-sufficient offline. If running the Python backend on your PC, enter its IP address to enable live WiFi syncing:",
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 12),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ipCtrl,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: "Host IP:Port",
                hintText: "e.g. 192.168.1.9:8000 or 10.0.2.2:8000",
                labelStyle: TextStyle(color: AppTheme.textMuted),
                filled: true,
                fillColor: Color(0xFF1E293B),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("CANCEL", style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            onPressed: () async {
              final nav = Navigator.of(ctx);
              final newIp = ipCtrl.text.trim();
              if (newIp.isNotEmpty) {
                await StorageService.saveBackendIp(newIp);
                setState(() => _backendIp = newIp);
              }
              if (mounted) nav.pop();
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.cyan),
            child: const Text("SAVE SYNC IP"),
          )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: AppTheme.gold));
    }

    final whyWall = (_profile["why_wall"] as List<dynamic>?) ?? OfflineData.defaultProfile["why_wall"] as List;
    final disciplineRules = (_profile["daily_discipline_rules"] as List<dynamic>?) ?? OfflineData.defaultProfile["daily_discipline_rules"] as List;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Brother's Cockpit", style: TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit, color: AppTheme.gold),
            onPressed: _showEditProfileDialog,
            tooltip: "Edit Profile",
          ),
          IconButton(
            icon: const Icon(Icons.settings_ethernet, color: AppTheme.cyan),
            onPressed: _showIpConfigDialog,
            tooltip: "Local Sync Settings",
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Hero Profile Banner
            _buildProfileHero(),
            const SizedBox(height: 16),

            // Kaustav's Letter to His Brother
            _buildKaustavLetterCard(),
            const SizedBox(height: 16),

            // The "Why Wall"
            const Text(
              "THE \"WHY\" WALL (CORE MOTIVATION)",
              style: TextStyle(color: AppTheme.gold, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1),
            ),
            const SizedBox(height: 10),
            _buildWhyWallCard(whyWall),
            const SizedBox(height: 16),

            // Daily Discipline Contract
            const Text(
              "DAILY DISCIPLINE PROTOCOL",
              style: TextStyle(color: AppTheme.emerald, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1),
            ),
            const SizedBox(height: 10),
            _buildDisciplineCard(disciplineRules),
            const SizedBox(height: 16),

            // Sync Status
            _buildSyncStatusCard(),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileHero() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.gold.withValues(alpha: 0.4)),
      ),
      child: Column(
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppTheme.gold.withValues(alpha: 0.15),
              border: Border.all(color: AppTheme.gold, width: 2),
            ),
            child: const Icon(Icons.school, color: AppTheme.gold, size: 36),
          ),
          const SizedBox(height: 12),
          Text(
            _profile["student_name"] ?? "Kaustav's Brother",
            style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 4),
          Text(
            _profile["target_college"] ?? "IIT Bombay CSE",
            style: const TextStyle(color: AppTheme.gold, fontSize: 13, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.emerald.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.emerald),
            ),
            child: Text(
              _profile["primary_goal"] ?? "JEE Advanced 2027 AIR 1 • CBSE 98.8%",
              style: const TextStyle(color: AppTheme.emerald, fontSize: 11, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildKaustavLetterCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.gold.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.favorite, color: AppTheme.rose, size: 18),
              const SizedBox(width: 8),
              const Text(
                "A PROMISE FROM YOUR BROTHER KAUSTAV",
                style: TextStyle(color: AppTheme.gold, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.5),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            _profile["brother_pledge"] ?? OfflineData.defaultProfile["brother_pledge"],
            style: const TextStyle(color: AppTheme.textPrimary, fontSize: 12, height: 1.5),
          ),
        ],
      ),
    );
  }

  Widget _buildWhyWallCard(List<dynamic> items) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Column(
        children: items.map((it) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.star, color: AppTheme.gold, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    it.toString(),
                    style: const TextStyle(color: Colors.white, fontSize: 12, height: 1.3),
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildDisciplineCard(List<dynamic> items) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Column(
        children: items.map((it) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.check_circle_outline, color: AppTheme.emerald, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    it.toString(),
                    style: const TextStyle(color: Colors.white, fontSize: 12, height: 1.3),
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildSyncStatusCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              const Icon(Icons.wifi, color: AppTheme.cyan, size: 18),
              const SizedBox(width: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("Offline Standalone Active", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
                  Text("Server Host: $_backendIp", style: const TextStyle(color: AppTheme.textMuted, fontSize: 10)),
                ],
              ),
            ],
          ),
          TextButton(
            onPressed: _showIpConfigDialog,
            child: const Text("CONFIGURE", style: TextStyle(color: AppTheme.cyan, fontSize: 11, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}
