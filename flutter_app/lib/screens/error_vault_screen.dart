import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/storage_service.dart';
import '../widgets/math_text.dart';

class ErrorVaultScreen extends StatefulWidget {
  const ErrorVaultScreen({super.key});

  @override
  State<ErrorVaultScreen> createState() => _ErrorVaultScreenState();
}

class _ErrorVaultScreenState extends State<ErrorVaultScreen> {
  List<Map<String, dynamic>> _errors = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadErrors();
  }

  Future<void> _loadErrors() async {
    final list = await StorageService.getErrors();
    if (mounted) {
      setState(() {
        _errors = list;
        _loading = false;
      });
    }
  }

  void _showAddErrorModal() {
    String selectedSubject = "Physics";
    String selectedCategory = "Calculation Slip";
    final chapterController = TextEditingController();
    final triggerLineController = TextEditingController();
    final remedyController = TextEditingController();

    final categories = [
      "Calculation Slip",
      "Misread Question / Condition",
      "Formula Recall Failure",
      "Conceptual Trap",
      "Time Panic / Rushed Algebra",
      "Incomplete Boundary Condition"
    ];

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppTheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setModalState) {
            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(ctx).viewInsets.bottom,
                left: 16,
                right: 16,
                top: 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "LOG TRIGGER-LINE MISTAKE AUTOPSY",
                      style: TextStyle(color: AppTheme.gold, fontSize: 13, fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 12),

                    // Subject Dropdown
                    Row(
                      children: [
                        const Text("Subject:", style: TextStyle(color: AppTheme.textSecondary)),
                        const SizedBox(width: 12),
                        DropdownButton<String>(
                          value: selectedSubject,
                          dropdownColor: AppTheme.card,
                          items: ["Physics", "Chemistry", "Mathematics", "CBSE Boards"]
                              .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                              .toList(),
                          onChanged: (val) {
                            if (val != null) setModalState(() => selectedSubject = val);
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),

                    // Error Category Dropdown
                    const Text("Error Category:", style: TextStyle(color: AppTheme.textSecondary, fontSize: 11)),
                    const SizedBox(height: 4),
                    DropdownButton<String>(
                      isExpanded: true,
                      value: selectedCategory,
                      dropdownColor: AppTheme.card,
                      items: categories.map((c) => DropdownMenuItem(value: c, child: Text(c, style: const TextStyle(fontSize: 13)))).toList(),
                      onChanged: (val) {
                        if (val != null) setModalState(() => selectedCategory = val);
                      },
                    ),
                    const SizedBox(height: 12),

                    // Chapter
                    TextField(
                      controller: chapterController,
                      style: const TextStyle(color: Colors.white),
                      decoration: const InputDecoration(
                        labelText: "Chapter / Concept Name",
                        labelStyle: TextStyle(color: AppTheme.textMuted),
                        filled: true,
                        fillColor: Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Trigger Line (Exact moment of failure)
                    TextField(
                      controller: triggerLineController,
                      maxLines: 2,
                      style: const TextStyle(color: Colors.white),
                      decoration: const InputDecoration(
                        labelText: "Trigger Line (The exact moment where error occurred)",
                        hintText: "e.g. Line 2: Wrote I = 1/2 mR^2 instead of 2/5 mR^2 for solid sphere",
                        hintStyle: TextStyle(color: AppTheme.textMuted, fontSize: 12),
                        labelStyle: TextStyle(color: AppTheme.textMuted),
                        filled: true,
                        fillColor: Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Corrective Rule
                    TextField(
                      controller: remedyController,
                      maxLines: 2,
                      style: const TextStyle(color: Colors.white),
                      decoration: const InputDecoration(
                        labelText: "AIR-1 Corrective Rule (How you will never repeat this)",
                        hintText: "e.g. Circle the word 'solid sphere' before choosing moment of inertia formula.",
                        hintStyle: TextStyle(color: AppTheme.textMuted, fontSize: 12),
                        labelStyle: TextStyle(color: AppTheme.textMuted),
                        filled: true,
                        fillColor: Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Submit Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: () async {
                          if (chapterController.text.trim().isEmpty || triggerLineController.text.trim().isEmpty) {
                            return;
                          }
                          final newErr = {
                            "subject": selectedSubject,
                            "category": selectedCategory,
                            "chapter": chapterController.text.trim(),
                            "trigger_line": triggerLineController.text.trim(),
                            "remedy": remedyController.text.trim(),
                            "date": DateTime.now().toIso8601String(),
                          };
                          final nav = Navigator.of(ctx);
                          await StorageService.addError(newErr);
                          if (mounted) {
                            nav.pop();
                            _loadErrors();
                          }
                        },
                        style: ElevatedButton.styleFrom(backgroundColor: AppTheme.rose),
                        child: const Text("LOCK INTO ERROR VAULT", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Error Vault & Autopsies", style: TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle, color: AppTheme.rose),
            onPressed: _showAddErrorModal,
            tooltip: "Log Mistake",
          )
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.rose))
          : _errors.isEmpty
              ? _buildZeroState()
              : _buildErrorList(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddErrorModal,
        backgroundColor: AppTheme.rose,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text("LOG MISTAKE", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ),
    );
  }

  Widget _buildZeroState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppTheme.rose.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.shield_outlined, color: AppTheme.rose, size: 54),
            ),
            const SizedBox(height: 16),
            const Text(
              "Zero Mistakes in Vault",
              style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              "Every mistake you encounter in mock tests is a 4-mark gift if identified early. Use the '+' button below to log your trigger-line autopsies and make them impossible to repeat.",
              textAlign: TextAlign.center,
              style: TextStyle(color: AppTheme.textMuted, fontSize: 13, height: 1.4),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _errors.length,
      itemBuilder: (context, index) {
        final err = _errors[index];
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.surface,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppTheme.rose.withValues(alpha: 0.3)),
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
                      color: AppTheme.rose.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      err["category"] ?? "Error",
                      style: const TextStyle(color: AppTheme.rose, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
                  Text(
                    err["subject"] ?? "",
                    style: const TextStyle(color: AppTheme.textMuted, fontSize: 11),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                err["chapter"] ?? "Chapter",
                style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text("TRIGGER MOMENT:", style: TextStyle(color: AppTheme.textMuted, fontSize: 9, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 2),
                    MathText(err["trigger_line"] ?? ""),
                  ],
                ),
              ),
              if (err["remedy"] != null && (err["remedy"] as String).isNotEmpty) ...[
                const SizedBox(height: 8),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check_circle_outline, color: AppTheme.emerald, size: 16),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        err["remedy"],
                        style: const TextStyle(color: AppTheme.emerald, fontSize: 12, height: 1.3),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}
