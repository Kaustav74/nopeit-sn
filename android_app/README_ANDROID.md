# 📱 Android Mobile Deployment Guide for JEE AIR-1 App

This project gives the student **two seamless ways** to use the application on an Android mobile phone:

---

## 🌟 Method 1: Instant 1-Tap PWA Mobile App (Zero Compile Needed)
The web application is engineered as a **Progressive Web App (PWA)** with a full service worker and mobile manifest.

1. Connect your Android phone to the same Wi-Fi network as your computer (or run on a cloud/remote URL).
2. Open Chrome on your Android mobile device and visit `http://<your-computer-ip>:8000` (e.g. `http://192.168.1.15:8000`).
3. You will see an **"Install App"** banner at the bottom or in the Chrome menu (⋮) -> **"Add to Home screen" / "Install App"**.
4. Tap **Install**: The app is installed as a standalone APK on your Android phone with the custom gold AIR-1 icon, full hardware acceleration, offline caching, and no browser URL bar!

---

## 🚀 Method 2: Native Android Studio Build
A complete, native Android application project is pre-configured in this `android_app` directory:

### Prerequisites:
- Android Studio Iguana / Jellyfish or newer
- Android SDK 34 (Android 14) and JDK 17

### Steps to Run:
1. Open Android Studio and select **Open** -> Select `d:\JEE Advanced AIR-1 APP\android_app`.
2. In `MainActivity.kt`, adjust `appUrl`:
   - If using the **Android Emulator**: leave as `"http://10.0.2.2:8000"`.
   - If deploying to a **Physical Android Phone**: set to your local IP `"http://192.168.x.x:8000"` or your deployed domain.
3. Click **Run (Shift+F10)** or connect your Android phone via USB and select your device.
4. To build an APK: In Android Studio, go to **Build** -> **Build Bundle(s) / APK(s)** -> **Build APK(s)**.
   - The generated APK will be in `app/build/outputs/apk/debug/app-debug.apk`.
