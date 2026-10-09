import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../data/offline_data.dart';
import '../widgets/math_text.dart';

class PlannerScreen extends StatelessWidget {
  const PlannerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final deadlines = OfflineData.masterDeadlines;
    final concepts = OfflineData.conceptGraph;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Omni-Planner & Concept Graph", style: TextStyle(fontWeight: FontWeight.w700)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Master Deadlines Header
            const Text(
              "MULTI-DEADLINE SCHEDULING ENGINE",
              style: TextStyle(color: AppTheme.cyan, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1),
            ),
            const SizedBox(height: 10),
            ...deadlines.map((d) => _buildDeadlineCard(d)),
            const SizedBox(height: 20),

            // Invisible Weakness Detector Banner
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.rose.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppTheme.rose.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.radar, color: AppTheme.rose, size: 24),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "INVISIBLE WEAKNESS DETECTOR ACTIVE",
                          style: TextStyle(color: AppTheme.rose, fontSize: 11, fontWeight: FontWeight.w800),
                        ),
                        SizedBox(height: 2),
                        Text(
                          "Tracks false mastery: When an Advanced question fails despite high confidence, the system traces back to root prerequisite gaps instead of blindly assigning random questions.",
                          style: TextStyle(color: AppTheme.textSecondary, fontSize: 11, height: 1.3),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Concept Dependency Map
            const Text(
              "CONCEPT DEPENDENCY GRAPH (ROOT-CAUSE TRACER)",
              style: TextStyle(color: AppTheme.gold, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1),
            ),
            const SizedBox(height: 10),
            ...concepts.map((c) => _buildConceptCard(c)),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildDeadlineCard(Map<String, dynamic> d) {
    Color badgeColor = AppTheme.cyan;
    if (d["priority"] == "Apex Goal") badgeColor = AppTheme.gold;
    if (d["type"] == "Board Exam") badgeColor = AppTheme.emerald;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: badgeColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: badgeColor.withValues(alpha: 0.4)),
            ),
            child: Column(
              children: [
                Text(
                  "${d['days_left']}",
                  style: TextStyle(color: badgeColor, fontSize: 16, fontWeight: FontWeight.w900),
                ),
                Text(
                  "DAYS",
                  style: TextStyle(color: badgeColor, fontSize: 9, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      d["title"],
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                    Text(
                      d["date"],
                      style: const TextStyle(color: AppTheme.textMuted, fontSize: 11),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  d["target"],
                  style: const TextStyle(color: AppTheme.textSecondary, fontSize: 11),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }

  Widget _buildConceptCard(Map<String, dynamic> c) {
    final status = c["status"] ?? "In Progress";
    Color statusColor = status == "Mastered" ? AppTheme.emerald : AppTheme.gold;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "${c['subject']} • ${c['chapter']}",
                style: const TextStyle(color: AppTheme.cyan, fontSize: 11, fontWeight: FontWeight.bold),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  status,
                  style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            c["name"],
            style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(8),
            ),
            child: MathText(c["formula"] ?? ""),
          ),
          if ((c["prerequisites"] as List).isNotEmpty) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.account_tree_outlined, color: AppTheme.textMuted, size: 14),
                const SizedBox(width: 4),
                Text(
                  "Prerequisites: ${(c['prerequisites'] as List).join(', ')}",
                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 10),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
