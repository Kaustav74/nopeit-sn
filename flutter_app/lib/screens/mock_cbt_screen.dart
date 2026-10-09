import 'dart:async';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../data/offline_data.dart';
import '../services/storage_service.dart';
import '../widgets/math_text.dart';

class MockCbtScreen extends StatefulWidget {
  const MockCbtScreen({super.key});

  @override
  State<MockCbtScreen> createState() => _MockCbtScreenState();
}

class _MockCbtScreenState extends State<MockCbtScreen> {
  final Map<String, dynamic> _exam = OfflineData.mockExams[0];
  late List<Map<String, dynamic>> _questions;
  int _currentQuestionIndex = 0;

  // Question state: question_id -> answers
  final Map<String, dynamic> _userAnswers = {};
  final Set<String> _markedForReview = {};
  final Set<String> _visitedQuestions = {};

  // 3-Pass Strategy Filter
  String _activePassFilter = "All"; // "All", "Pass 1: Harvest", "Pass 2: Heavy Lifting", "Pass 3: Risk"

  // Timers
  int _remainingExamSeconds = 180 * 60;
  Timer? _examTimer;
  int _questionSeconds = 0;
  Timer? _questionTimer;
  bool _bailoutAlertTriggered = false;

  final TextEditingController _numericalController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _questions = List<Map<String, dynamic>>.from(_exam["questions"]);
    _visitedQuestions.add(_questions[0]["id"]);
    _startTimers();
  }

  void _startTimers() {
    _examTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_remainingExamSeconds > 0) {
        setState(() => _remainingExamSeconds--);
      } else {
        _submitExam();
      }
    });

    _questionTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _questionSeconds++;
        if (_questionSeconds >= 90 && !_bailoutAlertTriggered) {
          _bailoutAlertTriggered = true;
        }
      });
    });
  }

  @override
  void dispose() {
    _examTimer?.cancel();
    _questionTimer?.cancel();
    _numericalController.dispose();
    super.dispose();
  }

  void _selectQuestion(int index) {
    setState(() {
      _currentQuestionIndex = index;
      _visitedQuestions.add(_questions[index]["id"]);
      _questionSeconds = 0;
      _bailoutAlertTriggered = false;
      _numericalController.text = _userAnswers[_questions[index]["id"]]?.toString() ?? "";
    });
  }

  void _toggleSingleOption(int optionIdx) {
    final qId = _questions[_currentQuestionIndex]["id"];
    setState(() {
      _userAnswers[qId] = optionIdx;
    });
  }

  void _toggleMultiOption(int optionIdx) {
    final qId = _questions[_currentQuestionIndex]["id"];
    setState(() {
      List<int> current = List<int>.from(_userAnswers[qId] ?? []);
      if (current.contains(optionIdx)) {
        current.remove(optionIdx);
      } else {
        current.add(optionIdx);
      }
      _userAnswers[qId] = current;
    });
  }

  void _saveNumerical() {
    final qId = _questions[_currentQuestionIndex]["id"];
    final text = _numericalController.text.trim();
    if (text.isNotEmpty) {
      final val = num.tryParse(text);
      if (val != null) {
        _userAnswers[qId] = val;
      }
    }
  }

  void _clearResponse() {
    final qId = _questions[_currentQuestionIndex]["id"];
    setState(() {
      _userAnswers.remove(qId);
      _numericalController.clear();
    });
  }

  void _toggleReview() {
    final qId = _questions[_currentQuestionIndex]["id"];
    setState(() {
      if (_markedForReview.contains(qId)) {
        _markedForReview.remove(qId);
      } else {
        _markedForReview.add(qId);
      }
    });
  }

  void _nextQuestion() {
    _saveNumerical();
    if (_currentQuestionIndex < _questions.length - 1) {
      _selectQuestion(_currentQuestionIndex + 1);
    }
  }

  void _submitExam() {
    _examTimer?.cancel();
    _questionTimer?.cancel();

    // Calculate score
    int score = 0;
    int correctCount = 0;
    int wrongCount = 0;

    for (final q in _questions) {
      final qId = q["id"];
      final userAns = _userAnswers[qId];
      final marking = q["marking"] as Map<String, dynamic>;

      if (userAns != null) {
        if (q["type"] == "single_choice") {
          if (userAns == q["correct_option"]) {
            score += marking["correct"] as int;
            correctCount++;
          } else {
            score += marking["negative"] as int;
            wrongCount++;
          }
        } else if (q["type"] == "numerical") {
          if (userAns == q["correct_numerical"]) {
            score += marking["correct"] as int;
            correctCount++;
          } else {
            wrongCount++;
          }
        } else if (q["type"] == "multi_correct") {
          final correctList = List<int>.from(q["correct_options"]);
          final userList = List<int>.from(userAns as List);
          if (userList.toSet().difference(correctList.toSet()).isEmpty &&
              userList.length == correctList.length) {
            score += marking["correct"] as int;
            correctCount++;
          } else if (userList.any((opt) => !correctList.contains(opt))) {
            score += marking["negative"] as int;
            wrongCount++;
          } else if (userList.isNotEmpty) {
            score += (marking["partial"] as int) * userList.length;
            correctCount++;
          }
        }
      }
    }

    StorageService.recordCbtAttempt({
      "exam_title": _exam["title"],
      "score": score,
      "total_marks": _exam["total_marks"],
      "correct_count": correctCount,
      "wrong_count": wrongCount,
      "total_questions": _questions.length,
      "attempted_count": _userAnswers.length,
      "date": DateTime.now().toIso8601String(),
    });

    _showResultDialog(score, correctCount, wrongCount);
  }

  void _showResultDialog(int score, int correct, int wrong) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.surface,
        title: const Text("CBT Exam Autopsy Complete", style: TextStyle(color: AppTheme.gold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Score: $score / ${_exam['total_marks']}", style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 10),
            Text("Correct: $correct  •  Wrong: $wrong  •  Unanswered: ${_questions.length - _userAnswers.length}", style: const TextStyle(color: AppTheme.textSecondary)),
            const SizedBox(height: 14),
            const Text("AIR-1 Execution Review:", style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.cyan)),
            const SizedBox(height: 6),
            const Text(
              "Every incorrect answer has been flagged for your Trigger-Line Autopsy. Never let a mistake recur.",
              style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context); // back to dashboard
            },
            child: const Text("CLOSE & LOG AUTOPSY"),
          ),
        ],
      ),
    );
  }

  String _formatDuration(int seconds) {
    final m = seconds ~/ 60;
    final s = seconds % 60;
    return "${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}";
  }

  @override
  Widget build(BuildContext context) {
    final currentQ = _questions[_currentQuestionIndex];
    final qId = currentQ["id"];
    final userAns = _userAnswers[qId];

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_exam["title"], style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
            Text(
              "Section: ${currentQ['section']} • ${currentQ['type'].toString().replaceAll('_', ' ').toUpperCase()}",
              style: const TextStyle(fontSize: 11, color: AppTheme.cyan),
            ),
          ],
        ),
        actions: [
          // Remaining time
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppTheme.cardBorder),
            ),
            child: Row(
              children: [
                const Icon(Icons.timer_outlined, color: AppTheme.gold, size: 16),
                const SizedBox(width: 4),
                Text(
                  _formatDuration(_remainingExamSeconds),
                  style: const TextStyle(color: AppTheme.gold, fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.grid_view_rounded, color: Colors.white),
            onPressed: _showQuestionPalette,
            tooltip: "Question Palette",
          )
        ],
      ),
      body: Column(
        children: [
          // 3-Pass Strategy & 90s Bailout Bar
          _buildTacticsStatusBar(currentQ),

          // Question Content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        "QUESTION ${_currentQuestionIndex + 1} OF ${_questions.length}",
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.gold.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          currentQ["pass_tag"] ?? "Pass 1: Harvest",
                          style: const TextStyle(color: AppTheme.gold, fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.surface,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppTheme.cardBorder),
                    ),
                    child: MathText(currentQ["question"] ?? ""),
                  ),
                  const SizedBox(height: 20),

                  // Option Selector depending on question type
                  if (currentQ["type"] == "single_choice") ...[
                    _buildSingleChoiceOptions(currentQ, userAns),
                  ] else if (currentQ["type"] == "multi_correct") ...[
                    _buildMultiCorrectOptions(currentQ, userAns),
                  ] else if (currentQ["type"] == "numerical") ...[
                    _buildNumericalInput(currentQ),
                  ],
                ],
              ),
            ),
          ),

          // Bottom Action Navigation
          _buildBottomCbtBar(),
        ],
      ),
    );
  }

  Widget _buildTacticsStatusBar(Map<String, dynamic> currentQ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      color: AppTheme.surface,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // 90s Bailout indicator
          Row(
            children: [
              Icon(
                _bailoutAlertTriggered ? Icons.warning_amber_rounded : Icons.hourglass_top,
                color: _bailoutAlertTriggered ? AppTheme.rose : AppTheme.cyan,
                size: 16,
              ),
              const SizedBox(width: 6),
              Text(
                "Time on Q: ${_formatDuration(_questionSeconds)}",
                style: TextStyle(
                  color: _bailoutAlertTriggered ? AppTheme.rose : Colors.white70,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (_bailoutAlertTriggered)
                Container(
                  margin: const EdgeInsets.only(left: 6),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(color: AppTheme.rose, borderRadius: BorderRadius.circular(4)),
                  child: const Text("BAILOUT WARNING", style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.w900)),
                ),
            ],
          ),

          // Marking scheme pill
          Text(
            "+${currentQ['marking']['correct']} / ${currentQ['marking']['negative'] ?? 0}",
            style: const TextStyle(color: AppTheme.emerald, fontSize: 11, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildSingleChoiceOptions(Map<String, dynamic> q, dynamic userAns) {
    final options = q["options"] as List<dynamic>;
    return Column(
      children: List.generate(options.length, (idx) {
        final isSelected = userAns == idx;
        return Container(
          margin: const EdgeInsets.only(bottom: 10),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.gold.withValues(alpha: 0.1) : AppTheme.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: isSelected ? AppTheme.gold : AppTheme.cardBorder),
          ),
          child: ListTile(
            leading: Radio<int>(
              value: idx,
              groupValue: userAns as int?,
              onChanged: (_) => _toggleSingleOption(idx),
              activeColor: AppTheme.gold,
            ),
            title: MathText(options[idx].toString()),
            onTap: () => _toggleSingleOption(idx),
          ),
        );
      }),
    );
  }

  Widget _buildMultiCorrectOptions(Map<String, dynamic> q, dynamic userAns) {
    final options = q["options"] as List<dynamic>;
    final selectedList = List<int>.from(userAns ?? []);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text("ONE OR MORE MAY BE CORRECT (+4 Full, +1/+2/+3 Partial, -2 Negative):",
            style: TextStyle(color: AppTheme.cyan, fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        ...List.generate(options.length, (idx) {
          final isSelected = selectedList.contains(idx);
          return Container(
            margin: const EdgeInsets.only(bottom: 10),
            decoration: BoxDecoration(
              color: isSelected ? AppTheme.cyan.withValues(alpha: 0.1) : AppTheme.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: isSelected ? AppTheme.cyan : AppTheme.cardBorder),
            ),
            child: CheckboxListTile(
              value: isSelected,
              onChanged: (_) => _toggleMultiOption(idx),
              activeColor: AppTheme.cyan,
              title: MathText(options[idx].toString()),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildNumericalInput(Map<String, dynamic> q) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text("ENTER NUMERICAL VALUE (+4 Correct, 0 Negative):",
            style: TextStyle(color: AppTheme.gold, fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        TextField(
          controller: _numericalController,
          keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
          style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
          decoration: InputDecoration(
            filled: true,
            fillColor: AppTheme.surface,
            hintText: "e.g. 5 or 3.14",
            hintStyle: const TextStyle(color: AppTheme.textMuted),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: AppTheme.cardBorder)),
            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: AppTheme.gold)),
          ),
          onChanged: (_) => _saveNumerical(),
        ),
      ],
    );
  }

  Widget _buildBottomCbtBar() {
    final isReviewed = _markedForReview.contains(_questions[_currentQuestionIndex]["id"]);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: const BoxDecoration(
        color: AppTheme.surface,
        border: Border(top: BorderSide(color: AppTheme.cardBorder)),
      ),
      child: Row(
        children: [
          OutlinedButton(
            onPressed: _clearResponse,
            style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 10)),
            child: const Text("Clear", style: TextStyle(fontSize: 11)),
          ),
          const SizedBox(width: 6),
          OutlinedButton(
            onPressed: _toggleReview,
            style: OutlinedButton.styleFrom(
              side: BorderSide(color: isReviewed ? AppTheme.purple : AppTheme.cardBorder),
              padding: const EdgeInsets.symmetric(horizontal: 10),
            ),
            child: Text(
              isReviewed ? "Reviewed" : "Mark Review",
              style: TextStyle(fontSize: 11, color: isReviewed ? AppTheme.purple : Colors.white),
            ),
          ),
          const Spacer(),
          ElevatedButton(
            onPressed: _nextQuestion,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.gold,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            ),
            child: const Text("Save & Next", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: 6),
          ElevatedButton(
            onPressed: _submitExam,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.emerald,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            ),
            child: const Text("Submit", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.black)),
          ),
        ],
      ),
    );
  }

  void _showQuestionPalette() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text("QUESTION PALETTE", style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.gold)),
                  Text("Filter: $_activePassFilter", style: const TextStyle(color: AppTheme.cyan, fontSize: 11)),
                ],
              ),
              const SizedBox(height: 10),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: ["All", "Pass 1: Harvest", "Pass 2: Heavy Lifting"].map((filter) {
                    final isSel = _activePassFilter == filter;
                    return Padding(
                      padding: const EdgeInsets.only(right: 6),
                      child: ChoiceChip(
                        label: Text(filter, style: TextStyle(fontSize: 10, color: isSel ? Colors.black : Colors.white70)),
                        selected: isSel,
                        selectedColor: AppTheme.gold,
                        backgroundColor: const Color(0xFF1E293B),
                        onSelected: (val) {
                          if (val) {
                            setState(() => _activePassFilter = filter);
                            Navigator.pop(context);
                            _showQuestionPalette();
                          }
                        },
                      ),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: List.generate(_questions.length, (idx) {
                  if (_activePassFilter != "All" &&
                      _questions[idx]["pass_tag"] != _activePassFilter) {
                    return const SizedBox.shrink();
                  }
                  final qId = _questions[idx]["id"];
                  final isAnswered = _userAnswers.containsKey(qId);
                  final isMarked = _markedForReview.contains(qId);
                  final isCurrent = idx == _currentQuestionIndex;

                  Color bg = const Color(0xFF1E293B);
                  if (isAnswered) bg = AppTheme.emerald;
                  if (isMarked) bg = AppTheme.purple;

                  return InkWell(
                    onTap: () {
                      Navigator.pop(context);
                      _selectQuestion(idx);
                    },
                    child: Container(
                      width: 40,
                      height: 40,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: bg,
                        borderRadius: BorderRadius.circular(8),
                        border: isCurrent ? Border.all(color: Colors.white, width: 2) : null,
                      ),
                      child: Text(
                        "${idx + 1}",
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                    ),
                  );
                }),
              ),
              const SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }
}
