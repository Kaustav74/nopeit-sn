import 'package:flutter_test/flutter_test.dart';
import 'package:jee_air1_app/main.dart';

void main() {
  testWidgets('App launches smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const JeeAir1App());
    expect(find.byType(JeeAir1App), findsOneWidget);
  });
}
