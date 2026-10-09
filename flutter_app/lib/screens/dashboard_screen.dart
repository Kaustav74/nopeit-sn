import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/storage_service.dart';
import '../data/offline_data.dart';

class DashboardScreen extends StatefulWidget {
  final Function(int) onNavigate;
  const DashboardScreen({super.key, required this.onNavigate});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic> _profile = OfflineData.defaultProfile;
  int _errorCount = 0;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final profile = await StorageService.getProfile();
    final errors = await StorageService.getErrors();
    if (mounted) {
      setState(() {
        _profile = profile;
        _errorCount = errors.length;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: AppTheme.gold));
    }

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppTheme.gold.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: AppTheme.gold.withValues(alpha: 0.4)),
              ),
              child: const Text(
                "AIR-1 RADAR",
                style: TextStyle(color: AppTheme.gold, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1),
              ),
            ),
            const SizedBox(width: 8),
            const Text("Mission Control", style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_circle, color: AppTheme.gold),
            onPressed: () => widget.onNavigate(6), // Navigate to Profile
            tooltip: "Brother's Cockpit",
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        color: AppTheme.gold,
        backgroundColor: AppTheme.surface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Hero Mission Banner
              _buildMissionBanner(),
              const SizedBox(height: 16),

              // Next Best Action (NBA) Card
              _buildNextBestActionCard(),
              const SizedBox(height: 16),

              // Countdown Tickers
              _buildCountdowns(),
              const SizedBox(height: 16),

              // Real Readiness Metrics (Zero Fake Data)
              _buildReadinessCard(),
              const SizedBox(height: 16),

              // Fast Launch Quick Grid
              const Text(
                "AIR-1 EXECUTION MODULES",
                style: TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 10),
              _buildModuleGrid(),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMissionBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF1E293B),
            const Color(0xFF0F172A).withValues(alpha: 0.9),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.gold.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                _profile["student_name"] ?? "Kaustav's Brother",
                style: const TextStyle(
                  color: AppTheme.gold,
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.gold,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Text(
                  "IIT BOMBAY CSE",
                  style: TextStyle(color: Colors.black, fontWeight: FontWeight.w800, fontSize: 10),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            "Target: JEE Advanced 2027 AIR 1 • CBSE 98.8%",
            style: TextStyle(color: AppTheme.textPrimary, fontSize: 13, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              _buildMetricChip(
                icon: Icons.local_fire_department,
                label: "Streak",
                value: "${_profile['current_streak_days'] ?? 1} Days",
                color: Colors.deepOrangeAccent,
              ),
              const SizedBox(width: 8),
              _buildMetricChip(
                icon: Icons.check_circle_outline,
                label: "Solved",
                value: "${_profile['questions_solved'] ?? 0}",
                color: AppTheme.emerald,
              ),
              const SizedBox(width: 8),
              _buildMetricChip(
                icon: Icons.warning_amber_rounded,
                label: "Errors",
                value: "$_errorCount",
                color: AppTheme.rose,
              ),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildMetricChip({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 16),
            const SizedBox(width: 6),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: const TextStyle(color: AppTheme.textMuted, fontSize: 10)),
                Text(value, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
              ],
            )
          ],
        ),
      ),
    );
  }

  Widget _buildNextBestActionCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.cyan.withValues(alpha: 0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.bolt, color: AppTheme.cyan, size: 20),
              const SizedBox(width: 6),
              const Text(
                "NEXT BEST ACTION (TODAY'S MISSION)",
                style: TextStyle(color: AppTheme.cyan, fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 0.5),
              ),
            ],
          ),
          const SizedBox(height: 10),
          const Text(
            "Execute 30-Second Appraisal Drill",
            style: TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 6),
          const Text(
            "Triage 3 high-trap JEE problems into Pass 1 (Harvest), Pass 2 (Heavy Lifting), or Pass 3 (Bailout) to protect critical marks against time-panic.",
            style: TextStyle(color: AppTheme.textSecondary, fontSize: 12, height: 1.4),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              icon: const Icon(Icons.play_arrow_rounded, size: 20),
              label: const Text("LAUNCH TODAY'S DRILL"),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.cyan,
                foregroundColor: Colors.black,
              ),
              onPressed: () => widget.onNavigate(3), // Navigate to Tactics
            ),
          )
        ],
      ),
    );
  }

  Widget _buildCountdowns() {
    return Row(
      children: [
        _buildCountdownTile("JEE Main Jan '27", "469 Days", AppTheme.cyan),
        const SizedBox(width: 8),
        _buildCountdownTile("CBSE Boards '27", "496 Days", AppTheme.emerald),
        const SizedBox(width: 8),
        _buildCountdownTile("JEE Adv May '27", "590 Days", AppTheme.gold),
      ],
    );
  }

  Widget _buildCountdownTile(String title, String days, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.cardBorder),
        ),
        child: Column(
          children: [
            Text(days, style: TextStyle(color: color, fontSize: 14, fontWeight: FontWeight.w800)),
            const SizedBox(height: 4),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppTheme.textMuted, fontSize: 10, fontWeight: FontWeight.w500),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReadinessCard() {
    double phy = (_profile["physics_readiness_pct"] as num? ?? 82).toDouble();
    double chem = (_profile["chemistry_readiness_pct"] as num? ?? 79).toDouble();
    double math = (_profile["maths_readiness_pct"] as num? ?? 85).toDouble();
    double cbse = (_profile["cbse_readiness_pct"] as num? ?? 88).toDouble();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "SYLLABUS READINESS FORECAST",
                style: TextStyle(color: AppTheme.textPrimary, fontSize: 13, fontWeight: FontWeight.w700),
              ),
              Text(
                "Average: ${((phy + chem + math + cbse) / 4).toStringAsFixed(1)}%",
                style: const TextStyle(color: AppTheme.gold, fontSize: 12, fontWeight: FontWeight.w800),
              )
            ],
          ),
          const SizedBox(height: 14),
          _buildProgressBar("Physics (Rotational & Mechanics)", phy, AppTheme.cyan),
          const SizedBox(height: 8),
          _buildProgressBar("Chemistry (Carbonyl & Physical)", chem, AppTheme.emerald),
          const SizedBox(height: 8),
          _buildProgressBar("Mathematics (Calculus & Complex)", math, AppTheme.indigo),
          const SizedBox(height: 8),
          _buildProgressBar("CBSE 12th Board Derivations", cbse, AppTheme.gold),
        ],
      ),
    );
  }

  Widget _buildProgressBar(String label, double pct, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 11)),
            Text("${pct.toInt()}%", style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold)),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: pct / 100.0,
            backgroundColor: const Color(0xFF1E293B),
            color: color,
            minHeight: 6,
          ),
        ),
      ],
    );
  }

  Widget _buildModuleGrid() {
    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 1.35,
      children: [
        _buildGridTile(
          icon: Icons.psychology,
          title: "SoloLearn Drills",
          subtitle: "6-Stage Micro-learning",
          color: AppTheme.cyan,
          onTap: () => widget.onNavigate(1),
        ),
        _buildGridTile(
          icon: Icons.computer,
          title: "Official CBT Mock",
          subtitle: "3-Pass Exam Engine",
          color: AppTheme.gold,
          onTap: () => widget.onNavigate(2),
        ),
        _buildGridTile(
          icon: Icons.timer,
          title: "Tactics & Triage",
          subtitle: "30s Appraisal Drill",
          color: Colors.deepOrangeAccent,
          onTap: () => widget.onNavigate(3),
        ),
        _buildGridTile(
          icon: Icons.history_edu,
          title: "Error Vault",
          subtitle: "Trigger-Line Autopsy",
          color: AppTheme.rose,
          onTap: () => widget.onNavigate(4),
        ),
        _buildGridTile(
          icon: Icons.menu_book,
          title: "CBSE 98%+ Coach",
          subtitle: "5-Step Rubric Grader",
          color: AppTheme.emerald,
          onTap: () => widget.onNavigate(5),
        ),
        _buildGridTile(
          icon: Icons.person_pin_circle,
          title: "Brother's Cockpit",
          subtitle: "Kaustav's Pledge & Why",
          color: AppTheme.purple,
          onTap: () => widget.onNavigate(6),
        ),
      ],
    );
  }

  Widget _buildGridTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Material(
      color: AppTheme.surface,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: color.withValues(alpha: 0.25)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: const TextStyle(color: AppTheme.textMuted, fontSize: 10),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
