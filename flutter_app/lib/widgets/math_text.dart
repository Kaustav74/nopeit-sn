import 'package:flutter/material.dart';
import 'package:flutter_math_fork/flutter_math.dart';

/// A robust widget that dynamically detects, parses, and renders
/// mathematical formulas using flutter_math_fork with graceful fallback.
/// Eliminates raw unparsed LaTeX from ever being visible to the user.
class MathText extends StatelessWidget {
  final String text;
  final TextStyle? textStyle;
  final TextStyle? mathStyle;
  final TextAlign textAlign;
  final bool isDisplay;

  const MathText(
    this.text, {
    super.key,
    this.textStyle,
    this.mathStyle,
    this.textAlign = TextAlign.start,
    this.isDisplay = false,
  });

  @override
  Widget build(BuildContext context) {
    if (text.isEmpty) return const SizedBox.shrink();

    final defaultTextStyle = textStyle ??
        Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.white,
              fontSize: 14,
              height: 1.45,
            ) ??
        const TextStyle(color: Colors.white, fontSize: 14, height: 1.45);

    final defaultMathStyle = mathStyle ??
        defaultTextStyle.copyWith(
          color: const Color(0xFFFBBF24), // Subtle gold for formulas
          fontSize: defaultTextStyle.fontSize != null ? defaultTextStyle.fontSize! * 1.05 : 15,
        );

    // If string is purely a LaTeX formula (e.g., starts with \ or enclosed in $$)
    final trimmed = text.trim();
    if ((trimmed.startsWith(r'$$') && trimmed.endsWith(r'$$')) ||
        (trimmed.startsWith(r'$') && trimmed.endsWith(r'$') && trimmed.length > 2 && !trimmed.substring(1, trimmed.length - 1).contains(r'$'))) {
      String rawFormula = trimmed;
      if (rawFormula.startsWith(r'$$') && rawFormula.endsWith(r'$$')) {
        rawFormula = rawFormula.substring(2, rawFormula.length - 2).trim();
      } else if (rawFormula.startsWith(r'$') && rawFormula.endsWith(r'$')) {
        rawFormula = rawFormula.substring(1, rawFormula.length - 1).trim();
      }
      return Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: _renderMath(rawFormula, defaultMathStyle, isDisplay: true),
        ),
      );
    }

    // Check if the entire string appears to be a pure formula without dollar delimiters
    // (e.g. "\frac{2}{7} mg \sin\theta up the incline" or "\sum \vec{T} \cdot \vec{a} = 0")
    if (_isPureFormula(trimmed)) {
      return _renderMath(trimmed, defaultMathStyle, isDisplay: isDisplay);
    }

    // Mixed text containing inline math like "... where $v_{cm} = R\omega$ is..."
    final spans = _parseMixedSpans(text, defaultTextStyle, defaultMathStyle);

    return RichText(
      textAlign: textAlign,
      text: TextSpan(children: spans),
    );
  }

  bool _isPureFormula(String s) {
    if (s.startsWith(r'\') && !s.contains('\n')) return true;
    final mathSignals = [
      r'\frac', r'\sqrt', r'\vec', r'\int', r'\sum', r'\oint',
      r'\alpha', r'\beta', r'\theta', r'\omega', r'\rho', r'\lambda',
      r'\Delta', r'\nabla', r'\varepsilon', r'\mu', r'\tau',
      r'\pm', r'\times', r'\cdot', r'\le', r'\ge', r'\approx',
      r'\rightarrow', r'\implies', r'^{', r'_{'
    ];
    int signalCount = 0;
    for (final sig in mathSignals) {
      if (s.contains(sig)) signalCount++;
    }
    return signalCount >= 2 && !s.contains(' ') && !s.contains('\n');
  }

  Widget _renderMath(String latex, TextStyle style, {bool isDisplay = false}) {
    // Sanitize common problematic escape characters or text annotations
    String sanitized = latex
        .replaceAll(r'\\', r'\')
        .replaceAll(r'\text {', r'\text{')
        .replaceAll(r'\mathrm {', r'\mathrm{');

    return Math.tex(
      sanitized,
      textStyle: style,
      mathStyle: isDisplay ? MathStyle.display : MathStyle.text,
      onErrorFallback: (err) {
        // Fallback clean unicode if KaTeX fails
        return Text(
          _cleanLatexToReadable(sanitized),
          style: style.copyWith(color: const Color(0xFFFBBF24)),
        );
      },
    );
  }

  List<InlineSpan> _parseMixedSpans(
    String input,
    TextStyle normalStyle,
    TextStyle mathStyle,
  ) {
    final List<InlineSpan> spans = [];
    final RegExp mathRegex = RegExp(r'(\$\$[\s\S]*?\$\$|\$[^\$\n]+?\$)');
    int lastIndex = 0;

    for (final Match match in mathRegex.allMatches(input)) {
      if (match.start > lastIndex) {
        final textChunk = input.substring(lastIndex, match.start);
        spans.addAll(_parseMarkdownText(textChunk, normalStyle));
      }

      final matchedStr = match.group(0)!;
      bool isBlock = matchedStr.startsWith(r'$$');
      String formula = isBlock
          ? matchedStr.substring(2, matchedStr.length - 2).trim()
          : matchedStr.substring(1, matchedStr.length - 1).trim();

      spans.add(
        WidgetSpan(
          alignment: PlaceholderAlignment.middle,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 2.0),
            child: _renderMath(formula, mathStyle, isDisplay: isBlock),
          ),
        ),
      );

      lastIndex = match.end;
    }

    if (lastIndex < input.length) {
      final remaining = input.substring(lastIndex);
      spans.addAll(_parseMarkdownText(remaining, normalStyle));
    }

    return spans;
  }

  List<InlineSpan> _parseMarkdownText(String text, TextStyle baseStyle) {
    final List<InlineSpan> spans = [];
    // Handle simple **bold** markings
    final RegExp boldRegex = RegExp(r'\*\*(.*?)\*\*');
    int last = 0;

    for (final Match m in boldRegex.allMatches(text)) {
      if (m.start > last) {
        spans.add(TextSpan(
          text: text.substring(last, m.start),
          style: baseStyle,
        ));
      }
      spans.add(TextSpan(
        text: m.group(1),
        style: baseStyle.copyWith(fontWeight: FontWeight.bold, color: Colors.white),
      ));
      last = m.end;
    }

    if (last < text.length) {
      spans.add(TextSpan(
        text: text.substring(last),
        style: baseStyle,
      ));
    }

    return spans;
  }

  String _cleanLatexToReadable(String s) {
    return s
        .replaceAll(r'\vec', '')
        .replaceAll(r'\Delta', 'Δ')
        .replaceAll(r'\theta', 'θ')
        .replaceAll(r'\omega', 'ω')
        .replaceAll(r'\alpha', 'α')
        .replaceAll(r'\beta', 'β')
        .replaceAll(r'\pi', 'π')
        .replaceAll(r'\times', '×')
        .replaceAll(r'\cdot', '·')
        .replaceAll(r'\frac', '')
        .replaceAll(r'\int', '∫')
        .replaceAll(r'\sum', '∑')
        .replaceAll(r'\pm', '±')
        .replaceAll(r'\le', '≤')
        .replaceAll(r'\ge', '≥')
        .replaceAll(r'\infty', '∞')
        .replaceAll('{', '')
        .replaceAll('}', '');
  }
}
