import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'web_cockpit_screen.dart';
import 'dashboard_screen.dart';
import 'sololearn_screen.dart';
import 'mock_cbt_screen.dart';
import 'tactics_screen.dart';
import 'error_vault_screen.dart';
import 'cbse_coach_screen.dart';
import 'profile_cockpit_screen.dart';

class HomeNavigation extends StatefulWidget {
  const HomeNavigation({super.key});

  @override
  State<HomeNavigation> createState() => _HomeNavigationState();
}

class _HomeNavigationState extends State<HomeNavigation> {
  int _currentIndex = 0;

  void _onNavigate(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> screens = [
      WebCockpitScreen(onOpenNativeModules: () => _onNavigate(1)),
      DashboardScreen(onNavigate: (idx) => _onNavigate(idx + 1)),
      const SoloLearnScreen(),
      const MockCbtScreen(),
      const TacticsScreen(),
      const ErrorVaultScreen(),
      const CbseCoachScreen(),
      const ProfileCockpitScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex >= 7 ? 0 : _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        backgroundColor: AppTheme.surface,
        selectedItemColor: AppTheme.gold,
        unselectedItemColor: AppTheme.textMuted,
        selectedFontSize: 10,
        unselectedFontSize: 9,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.language),
            activeIcon: Icon(Icons.language, color: AppTheme.gold),
            label: "All Features",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard, color: AppTheme.gold),
            label: "Mission",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.psychology_outlined),
            activeIcon: Icon(Icons.psychology, color: AppTheme.gold),
            label: "SoloLearn",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.computer_outlined),
            activeIcon: Icon(Icons.computer, color: AppTheme.gold),
            label: "CBT Mock",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.timer_outlined),
            activeIcon: Icon(Icons.timer, color: AppTheme.gold),
            label: "Tactics",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history_edu_outlined),
            activeIcon: Icon(Icons.history_edu, color: AppTheme.gold),
            label: "Errors",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person, color: AppTheme.gold),
            label: "Profile",
          ),
        ],
      ),
    );
  }
}
