import 'dart:async';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../data/offline_data.dart';
import '../widgets/math_text.dart';

class TacticsScreen extends StatefulWidget {
  const TacticsScreen({super.key});

  @override
  State<TacticsScreen> createState() => _TacticsScreenState();
}

class _TacticsScreenState extends State<TacticsScreen> {
  int _currentDrillIndex = 0;
  int _secondsLeft = 30;
  Timer? _drillTimer;
  String? _userChosenPass;
  bool _evaluated = false;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  void _startTimer() {
    _drillTimer?.cancel();
    setState(() {
      _secondsLeft = 30;
      _userChosenPass = null;
      _evaluated = false;
    });
    _drillTimer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (_secondsLeft > 0) {
        setState(() => _secondsLeft--);
      } else {
        t.cancel();
      }
    });
  }

  @override
  void dispose() {
    _drillTimer?.cancel();
    super.dispose();
  }

  void _selectPass(String pass) {
    if (_evaluated) return;
    _drillTimer?.cancel();
    setState(() {
      _userChosenPass = pass;
      _evaluated = true;
    });
  }

  void _nextDrill() {
    final drills = OfflineData.triageDrills;
    setState(() {
      _currentDrillIndex = (_currentDrillIndex + 1) % drills.length;
    });
    _startTimer();
  }

  @override
  Widget build(BuildContext context) {
    final drills = OfflineData.triageDrills;
    final currentDrill = drills[_currentDrillIndex];

    return Scaffold(
      appBar: AppBar(
        title: const Text("Tactics & Endurance Engine", style: TextStyle(fontWeight: FontWeight.w700)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 30-Second Appraisal Drill Header
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.gold.withValues(alpha: 0.4)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.flash_on, color: AppTheme.gold, size: 18),
                          const SizedBox(width: 6),
                          Text(
                            "30-SECOND APPRAISAL DRILL (${_currentDrillIndex + 1}/${drills.length})",
                            style: const TextStyle(color: AppTheme.gold, fontSize: 11, fontWeight: FontWeight.w800),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: _secondsLeft <= 5 ? AppTheme.rose.withValues(alpha: 0.2) : AppTheme.gold.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: _secondsLeft <= 5 ? AppTheme.rose : AppTheme.gold),
                        ),
                        child: Text(
                          "00:${_secondsLeft.toString().padLeft(2, '0')}",
                          style: TextStyle(
                            color: _secondsLeft <= 5 ? AppTheme.rose : AppTheme.gold,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      )
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    "Rapidly inspect the question below. Do NOT solve completely. Choose which exam pass this problem belongs to:",
                    style: TextStyle(color: AppTheme.textSecondary, fontSize: 12),
                  ),
                  const SizedBox(height: 14),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: MathText(currentDrill["question"]),
                  ),
                  const SizedBox(height: 16),

                  // 3 Pass Option Buttons
                  _buildPassButton("Pass 1: Harvest", "Instant solution, formula direct, guaranteed marks", currentDrill),
                  const SizedBox(height: 8),
                  _buildPassButton("Pass 2: Heavy Lifting", "Known concepts, multi-step calculation, time required", currentDrill),
                  const SizedBox(height: 8),
                  _buildPassButton("Pass 3: Calculated Risk", "High trap density, partial marking exploitation only", currentDrill),

                  if (_evaluated) ...[
                    const SizedBox(height: 16),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: _userChosenPass == currentDrill["correct_pass"]
                            ? AppTheme.emerald.withValues(alpha: 0.15)
                            : AppTheme.rose.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _userChosenPass == currentDrill["correct_pass"] ? AppTheme.emerald : AppTheme.rose,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                _userChosenPass == currentDrill["correct_pass"] ? Icons.check_circle : Icons.cancel,
                                color: _userChosenPass == currentDrill["correct_pass"] ? AppTheme.emerald : AppTheme.rose,
                                size: 18,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _userChosenPass == currentDrill["correct_pass"] ? "OPTIMAL TRIAGE DECISION!" : "SUBOPTIMAL TRIAGE",
                                style: TextStyle(
                                  color: _userChosenPass == currentDrill["correct_pass"] ? AppTheme.emerald : AppTheme.rose,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            "Strategic Analysis: ${currentDrill['reasoning']}",
                            style: const TextStyle(color: Colors.white, fontSize: 12, height: 1.4),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _nextDrill,
                        child: const Text("NEXT TRIAGE DRILL"),
                      ),
                    )
                  ]
                ],
              ),
            ),
            const SizedBox(height: 20),

            // 6-Hour Dual Paper Endurance Protocol
            const Text(
              "6-HOUR DUAL-PAPER ENDURANCE PROTOCOL",
              style: TextStyle(color: AppTheme.cyan, fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 1),
            ),
            const SizedBox(height: 10),
            _buildEnduranceProtocolCard(),
            const SizedBox(height: 20),

            // God Mode Cross-Topic Matrix
            const Text(
              "\"GOD MODE\" CROSS-TOPIC SYNTHESIS MATRIX",
              style: TextStyle(color: AppTheme.purple, fontSize: 12, fontWeight: FontWeight.w800, letterSpacing: 1),
            ),
            const SizedBox(height: 10),
            _buildGodModeCard(),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildPassButton(String passName, String description, Map<String, dynamic> drill) {
    bool isSelected = _userChosenPass == passName;
    bool isCorrect = drill["correct_pass"] == passName;

    Color border = AppTheme.cardBorder;
    Color bg = const Color(0xFF1E293B);

    if (_evaluated) {
      if (isCorrect) {
        border = AppTheme.emerald;
        bg = AppTheme.emerald.withValues(alpha: 0.15);
      } else if (isSelected && !isCorrect) {
        border = AppTheme.rose;
        bg = AppTheme.rose.withValues(alpha: 0.15);
      }
    } else if (isSelected) {
      border = AppTheme.gold;
    }

    return InkWell(
      onTap: () => _selectPass(passName),
      borderRadius: BorderRadius.circular(10),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(passName, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
            const SizedBox(height: 2),
            Text(description, style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
          ],
        ),
      ),
    );
  }

  Widget _buildEnduranceProtocolCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildTimelineStep(
            time: "09:00 - 12:00",
            title: "Paper 1 Execution",
            desc: "High cortisol peak. Harvest rapid mechanics and physical chemistry marks.",
            color: AppTheme.cyan,
          ),
          const SizedBox(height: 12),
          _buildTimelineStep(
            time: "12:00 - 14:30",
            title: "2.5h Cognitive Recalibration (Critical)",
            desc: "Zero discussion of Paper 1. Hydrate with electrolyte water and light complex carbs. 20 min closed-eye meditation.",
            color: AppTheme.gold,
          ),
          const SizedBox(height: 12),
          _buildTimelineStep(
            time: "14:30 - 17:30",
            title: "Paper 2 Mental Stamina Defense",
            desc: "Combat mental fatigue. Re-check algebra twice. Enforce 90-second bailout strictly.",
            color: AppTheme.emerald,
          ),
        ],
      ),
    );
  }

  Widget _buildTimelineStep({
    required String time,
    required String title,
    required String desc,
    required Color color,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: color),
          ),
          child: Text(time, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 2),
              Text(desc, style: const TextStyle(color: AppTheme.textMuted, fontSize: 11, height: 1.3)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildGodModeCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.purple.withValues(alpha: 0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.hub, color: AppTheme.purple, size: 20),
              const SizedBox(width: 8),
              const Text("Rotational Mechanics + EMI + Calculus", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            "A conducting rod of mass \$m\$ rolls down two inclined conducting rails in a uniform magnetic field \$\\vec{B}\$. Induced EMF creates terminal rolling velocity.",
            style: TextStyle(color: AppTheme.textSecondary, fontSize: 12, height: 1.4),
          ),
          const SizedBox(height: 10),
          MathText(r"\vec{\tau}_{net} = \vec{\tau}_g - \vec{\tau}_B = I\vec{\alpha}, \quad \mathcal{E} = B L v"),
        ],
      ),
    );
  }
}
