import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../services/embedded_server.dart';
import '../services/storage_service.dart';
import '../theme/app_theme.dart';

class WebCockpitScreen extends StatefulWidget {
  final VoidCallback? onOpenNativeModules;
  const WebCockpitScreen({super.key, this.onOpenNativeModules});

  @override
  State<WebCockpitScreen> createState() => _WebCockpitScreenState();
}

class _WebCockpitScreenState extends State<WebCockpitScreen> {
  late final WebViewController _controller;
  bool _serverReady = false;
  bool _pageLoading = true;
  String _backendIp = "192.168.1.9:8000";

  @override
  void initState() {
    super.initState();
    _initApp();
  }

  Future<void> _initApp() async {
    final ip = await StorageService.getBackendIp();
    setState(() => _backendIp = ip);

    // 1. Start internal HTTP server
    final port = await EmbeddedServer.start();

    // 2. Setup WebView controller
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(AppTheme.background)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (_) {
            if (mounted) setState(() => _pageLoading = true);
          },
          onPageFinished: (_) {
            if (mounted) setState(() => _pageLoading = false);
          },
          onWebResourceError: (error) {
            debugPrint("WebView resource error: ${error.description}");
          },
        ),
      );

    // 3. Load from local embedded server
    await _controller.loadRequest(Uri.parse("http://127.0.0.1:$port"));

    if (mounted) {
      setState(() {
        _serverReady = true;
      });
    }
  }

  void _showServerConfig() {
    final ipCtrl = TextEditingController(text: _backendIp);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.surface,
        title: const Text("AIR-1 Server Host IP", style: TextStyle(color: AppTheme.gold, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "All features, tabs, notes, and engines are baked 100% inside this APK.",
              style: TextStyle(color: Colors.white70, fontSize: 12),
            ),
            const SizedBox(height: 8),
            const Text(
              "To sync with the Python backend on your PC, enter its Wi-Fi IP address:",
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 11),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ipCtrl,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: "Host IP:Port",
                hintText: "192.168.1.9:8000",
                labelStyle: TextStyle(color: AppTheme.textMuted),
                filled: true,
                fillColor: Color(0xFF1E293B),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("CANCEL", style: TextStyle(color: AppTheme.textMuted)),
          ),
          ElevatedButton(
            onPressed: () async {
              final nav = Navigator.of(ctx);
              final newIp = ipCtrl.text.trim();
              if (newIp.isNotEmpty) {
                await StorageService.saveBackendIp(newIp);
                setState(() => _backendIp = newIp);
                _controller.reload();
              }
              if (mounted) nav.pop();
            },
            child: const Text("CONNECT & RELOAD"),
          )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) async {
        if (didPop) return;
        if (_serverReady && await _controller.canGoBack()) {
          _controller.goBack();
          return;
        }
        if (context.mounted) {
          Navigator.of(context).maybePop();
        }
      },
      child: Scaffold(
        appBar: AppBar(
          titleSpacing: 12,
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.gold.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: AppTheme.gold.withValues(alpha: 0.5)),
                ),
                child: const Text(
                  "AIR-1 PRO",
                  style: TextStyle(color: AppTheme.gold, fontSize: 10, fontWeight: FontWeight.w900, letterSpacing: 1),
                ),
              ),
              const SizedBox(width: 8),
              const Text("JEE Advanced & CBSE Cockpit", style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
            ],
          ),
          actions: [
            // Live IP connection chip
            InkWell(
              onTap: _showServerConfig,
              borderRadius: BorderRadius.circular(8),
              child: Container(
                margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 4),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.cardBorder),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.wifi, color: AppTheme.cyan, size: 14),
                    const SizedBox(width: 4),
                    Text(
                      _backendIp.split(':').first,
                      style: const TextStyle(color: AppTheme.cyan, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.refresh, color: Colors.white, size: 20),
              onPressed: () => _controller.reload(),
              tooltip: "Reload App",
            ),
            if (widget.onOpenNativeModules != null)
              IconButton(
                icon: const Icon(Icons.dashboard_customize_outlined, color: AppTheme.gold, size: 20),
                onPressed: widget.onOpenNativeModules,
                tooltip: "Quick Focus Drills",
              ),
          ],
        ),
        body: Stack(
          children: [
            if (_serverReady)
              WebViewWidget(controller: _controller)
            else
              const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(color: AppTheme.gold),
                    SizedBox(height: 16),
                    Text("Launching AIR-1 Cockpit...", style: TextStyle(color: AppTheme.gold, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            if (_pageLoading)
              const LinearProgressIndicator(
                backgroundColor: Colors.transparent,
                color: AppTheme.gold,
                minHeight: 2.5,
              ),
          ],
        ),
      ),
    );
  }
}
