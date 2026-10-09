import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../data/offline_data.dart';
import '../widgets/math_text.dart';

class CbseCoachScreen extends StatefulWidget {
  const CbseCoachScreen({super.key});

  @override
  State<CbseCoachScreen> createState() => _CbseCoachScreenState();
}

class _CbseCoachScreenState extends State<CbseCoachScreen> {
  int _selectedDrillIndex = 0;
  final Set<int> _checkedSteps = {};

  @override
  Widget build(BuildContext context) {
    final drills = OfflineData.cbseRubricDrills;
    final currentDrill = drills[_selectedDrillIndex];
    final steps = currentDrill["rubric_steps"] as List<dynamic>;

    double totalScore = 0;
    for (int i = 0; i < steps.length; i++) {
      if (_checkedSteps.contains(i)) {
        totalScore += (steps[i]["marks"] as num).toDouble();
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("CBSE 98%+ Answer-Writing Coach", style: TextStyle(fontWeight: FontWeight.w700)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Derivation selector tabs
            Container(
              height: 44,
              margin: const EdgeInsets.only(bottom: 16),
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: drills.length,
                itemBuilder: (context, idx) {
                  final isSelected = idx == _selectedDrillIndex;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text(drills[idx]["id"].toString().replaceAll('_', ' ').toUpperCase()),
                      selected: isSelected,
                      onSelected: (_) {
                        setState(() {
                          _selectedDrillIndex = idx;
                          _checkedSteps.clear();
                        });
                      },
                      selectedColor: AppTheme.emerald,
                      backgroundColor: AppTheme.surface,
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.black : Colors.white70,
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                  );
                },
              ),
            ),

            // Question Banner
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.emerald.withValues(alpha: 0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.emerald.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          "${currentDrill['marks']} MARKS LONG DERIVATION",
                          style: const TextStyle(color: AppTheme.emerald, fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      ),
                      Text(
                        "Self-Audit: ${totalScore.toStringAsFixed(1)} / ${currentDrill['marks']}",
                        style: const TextStyle(color: AppTheme.gold, fontSize: 13, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  MathText(currentDrill["question"]),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // 5-Step Rubric Checklist
            const Text(
              "OFFICIAL 5-STEP MARKING RUBRIC (STEP-LOSS PREVENTER)",
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.5),
            ),
            const SizedBox(height: 10),

            ...List.generate(steps.length, (idx) {
              final step = steps[idx];
              final isChecked = _checkedSteps.contains(idx);

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: isChecked ? AppTheme.emerald.withValues(alpha: 0.1) : AppTheme.surface,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: isChecked ? AppTheme.emerald : AppTheme.cardBorder,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Checkbox(
                          value: isChecked,
                          activeColor: AppTheme.emerald,
                          onChanged: (val) {
                            setState(() {
                              if (val == true) {
                                _checkedSteps.add(idx);
                              } else {
                                _checkedSteps.remove(idx);
                              }
                            });
                          },
                        ),
                        Expanded(
                          child: Text(
                            step["step_name"],
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1E293B),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            "+${step['marks']} M",
                            style: const TextStyle(color: AppTheme.gold, fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        )
                      ],
                    ),
                    const SizedBox(height: 6),
                    Padding(
                      padding: const EdgeInsets.only(left: 48, right: 8),
                      child: MathText(step["content"]),
                    ),
                  ],
                ),
              );
            }),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
