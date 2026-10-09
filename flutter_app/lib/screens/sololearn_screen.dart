import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../data/offline_data.dart';
import '../services/storage_service.dart';
import '../widgets/math_text.dart';

class SoloLearnScreen extends StatefulWidget {
  const SoloLearnScreen({super.key});

  @override
  State<SoloLearnScreen> createState() => _SoloLearnScreenState();
}

class _SoloLearnScreenState extends State<SoloLearnScreen> {
  int _selectedModuleIndex = 0;
  int _currentStepIndex = 0;
  int? _selectedOption;
  bool _submitted = false;
  int _earnedXp = 0;
  Map<String, int> _progress = {};

  @override
  void initState() {
    super.initState();
    _loadProgress();
  }

  Future<void> _loadProgress() async {
    final prog = await StorageService.getSoloLearnProgress();
    setState(() {
      _progress = prog;
      final modId = OfflineData.soloLearnModules[_selectedModuleIndex]["module_id"];
      _currentStepIndex = prog[modId] ?? 0;
    });
  }

  void _onSelectModule(int index) {
    setState(() {
      _selectedModuleIndex = index;
      final modId = OfflineData.soloLearnModules[index]["module_id"];
      _currentStepIndex = _progress[modId] ?? 0;
      _selectedOption = null;
      _submitted = false;
    });
  }

  void _submitAnswer(int correctOption, int xp) {
    setState(() {
      _submitted = true;
      if (_selectedOption == correctOption) {
        _earnedXp += xp;
      }
    });
  }

  void _nextStep(int totalSteps, String moduleId) {
    if (_currentStepIndex < totalSteps - 1) {
      setState(() {
        _currentStepIndex++;
        _selectedOption = null;
        _submitted = false;
      });
      StorageService.updateSoloLearnStep(moduleId, _currentStepIndex);
    } else {
      // Completed module
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Module Completed! +$_earnedXp XP added to your AIR-1 Mastery bank!"),
          backgroundColor: AppTheme.emerald,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final modules = OfflineData.soloLearnModules;
    final currentModule = modules[_selectedModuleIndex];
    final steps = currentModule["steps"] as List<dynamic>;
    final step = steps[_currentStepIndex.clamp(0, steps.length - 1)] as Map<String, dynamic>;
    final isConcept = step["type"] == "concept_nugget";

    return Scaffold(
      appBar: AppBar(
        title: const Text("SoloLearn Micro-Drills", style: TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.gold.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.gold),
            ),
            child: Row(
              children: [
                const Icon(Icons.bolt, color: AppTheme.gold, size: 16),
                const SizedBox(width: 4),
                Text(
                  "$_earnedXp XP",
                  style: const TextStyle(color: AppTheme.gold, fontWeight: FontWeight.bold, fontSize: 12),
                ),
              ],
            ),
          )
        ],
      ),
      body: Column(
        children: [
          // Module Selector Tabs
          Container(
            height: 52,
            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
            color: AppTheme.surface,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: modules.length,
              itemBuilder: (context, index) {
                final mod = modules[index];
                final isSelected = index == _selectedModuleIndex;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(mod["subject"]),
                    selected: isSelected,
                    onSelected: (_) => _onSelectModule(index),
                    selectedColor: AppTheme.gold,
                    backgroundColor: AppTheme.card,
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.black : Colors.white70,
                      fontWeight: FontWeight.w700,
                      fontSize: 12,
                    ),
                  ),
                );
              },
            ),
          ),

          // Step Progress Bar
          LinearProgressIndicator(
            value: (_currentStepIndex + 1) / steps.length,
            backgroundColor: const Color(0xFF1E293B),
            color: AppTheme.gold,
            minHeight: 4,
          ),

          // Content Area
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Topic Tag
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        currentModule["topic"].toString().toUpperCase(),
                        style: const TextStyle(
                          color: AppTheme.cyan,
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 1,
                        ),
                      ),
                      Text(
                        "Step ${_currentStepIndex + 1} of ${steps.length}",
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 11),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    step["title"] ?? currentModule["title"],
                    style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),

                  // Display either Concept Nugget or Active Recall Question
                  if (isConcept) ...[
                    _buildConceptView(step),
                  ] else ...[
                    _buildActiveRecallView(step),
                  ],
                ],
              ),
            ),
          ),

          // Bottom Action Navigation
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              color: AppTheme.surface,
              border: Border(top: BorderSide(color: AppTheme.cardBorder)),
            ),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: (!isConcept && !_submitted)
                    ? (_selectedOption != null
                        ? () => _submitAnswer(step["correct_option"] as int, step["xp"] as int? ?? 25)
                        : null)
                    : () => _nextStep(steps.length, currentModule["module_id"]),
                style: ElevatedButton.styleFrom(
                  backgroundColor: (!isConcept && !_submitted) ? AppTheme.cyan : AppTheme.gold,
                ),
                child: Text(
                  (!isConcept && !_submitted)
                      ? "CHECK ANSWER"
                      : (_currentStepIndex < steps.length - 1 ? "CONTINUE TO NEXT STEP" : "FINISH MODULE"),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConceptView(Map<String, dynamic> step) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: MathText(step["content"] ?? ""),
        ),
        const SizedBox(height: 16),
        if (step["key_takeaway"] != null)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.gold.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.gold.withValues(alpha: 0.3)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.lightbulb_outline, color: AppTheme.gold, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "AIR-1 KEY TAKEAWAY",
                        style: TextStyle(color: AppTheme.gold, fontSize: 11, fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 4),
                      MathText(step["key_takeaway"]),
                    ],
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildActiveRecallView(Map<String, dynamic> step) {
    final options = (step["options"] as List<dynamic>?) ?? [];
    final correctOption = step["correct_option"] as int? ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (step["pyq_source"] != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.purple.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: AppTheme.purple.withValues(alpha: 0.4)),
            ),
            child: Text(
              step["pyq_source"],
              style: const TextStyle(color: Color(0xFFC084FC), fontSize: 11, fontWeight: FontWeight.bold),
            ),
          ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.cardBorder),
          ),
          child: MathText(step["question"] ?? ""),
        ),
        const SizedBox(height: 16),
        const Text(
          "SELECT YOUR ANSWER:",
          style: TextStyle(color: AppTheme.textSecondary, fontSize: 11, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        ...List.generate(options.length, (idx) {
          final isSelected = _selectedOption == idx;
          Color borderColor = AppTheme.cardBorder;
          Color bgColor = AppTheme.surface;

          if (_submitted) {
            if (idx == correctOption) {
              borderColor = AppTheme.emerald;
              bgColor = AppTheme.emerald.withValues(alpha: 0.15);
            } else if (isSelected && idx != correctOption) {
              borderColor = AppTheme.rose;
              bgColor = AppTheme.rose.withValues(alpha: 0.15);
            }
          } else if (isSelected) {
            borderColor = AppTheme.gold;
            bgColor = AppTheme.gold.withValues(alpha: 0.1);
          }

          return Container(
            margin: const EdgeInsets.only(bottom: 10),
            decoration: BoxDecoration(
              color: bgColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderColor, width: isSelected || (_submitted && idx == correctOption) ? 1.5 : 1),
            ),
            child: InkWell(
              borderRadius: BorderRadius.circular(12),
              onTap: _submitted
                  ? null
                  : () {
                      setState(() {
                        _selectedOption = idx;
                      });
                    },
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Row(
                  children: [
                    Container(
                      width: 26,
                      height: 26,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isSelected ? AppTheme.gold : const Color(0xFF1E293B),
                        border: Border.all(color: borderColor),
                      ),
                      child: Text(
                        String.fromCharCode(65 + idx), // A, B, C, D
                        style: TextStyle(
                          color: isSelected ? Colors.black : Colors.white70,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: MathText(options[idx].toString()),
                    ),
                  ],
                ),
              ),
            ),
          );
        }),
        if (_submitted) ...[
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: _selectedOption == correctOption
                  ? AppTheme.emerald.withValues(alpha: 0.1)
                  : AppTheme.rose.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: _selectedOption == correctOption ? AppTheme.emerald : AppTheme.rose,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      _selectedOption == correctOption ? Icons.check_circle : Icons.cancel,
                      color: _selectedOption == correctOption ? AppTheme.emerald : AppTheme.rose,
                      size: 18,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      _selectedOption == correctOption ? "CORRECT! +${step['xp'] ?? 25} XP" : "INCORRECT",
                      style: TextStyle(
                        color: _selectedOption == correctOption ? AppTheme.emerald : AppTheme.rose,
                        fontWeight: FontWeight.w800,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text("EXPLANATION & PROOF:", style: TextStyle(color: AppTheme.textMuted, fontSize: 10, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                MathText(step["explanation"] ?? ""),
              ],
            ),
          ),
        ]
      ],
    );
  }
}
