# 📱 BotMR Mobile App Build Guide

## 🚀 Quick Testing on Real Phone

### Method 1: Expo Go (Fastest - 2 minutes)

1. **Install Expo Go** on your phone:
   - 📱 **iPhone**: [Download from App Store](https://apps.apple.com/app/expo-go/id982107779)
   - 🤖 **Android**: [Download from Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. **Start the development server**:
   ```bash
   cd frontend
   npm start
   ```

3. **Scan QR Code**:
   - **iPhone**: Open camera app and scan the QR code
   - **Android**: Open Expo Go app and scan the QR code
   
4. **Done!** 🎉 The app will load on your phone in ~30 seconds

---

## 🏗️ Development Build (More Features)

### Prerequisites
```bash
npm install -g @expo/eas-cli
```

### Step 1: Setup EAS (One-time)
```bash
cd frontend
eas login
eas build:configure
```

### Step 2: Build for Your Device

#### Android APK (No Google Play Developer Account needed)
```bash
# Development build (for testing)
eas build --platform android --profile development

# Preview build (for sharing)
eas build --platform android --profile preview
```

#### iOS (Requires Apple Developer Account - $99/year)
```bash
# Development build
eas build --platform ios --profile development

# Preview build
eas build --platform ios --profile preview
```

### Step 3: Install on Device
1. EAS will provide a download link
2. Click the link on your phone to install
3. **Android**: Enable "Install from Unknown Sources"
4. **iOS**: Trust the developer certificate in Settings

---

## 📦 Production Builds (App Stores)

### Android Play Store
```bash
# Build AAB for Play Store
eas build --platform android --profile production

# Submit to Play Store
eas submit --platform android
```

### iOS App Store
```bash
# Build for App Store
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

---

## 🔧 Configuration for Your Backend

### Update API URL

1. **For Local Testing** (Backend running on your computer):
   ```bash
   # In frontend/.env
   EXPO_PUBLIC_API_URL=http://YOUR_COMPUTER_IP:8001
   ```

2. **For Heroku Deployment**:
   ```bash
   # In frontend/.env
   EXPO_PUBLIC_API_URL=https://your-app-name.herokuapp.com
   ```

3. **Find Your Computer's IP**:
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet 192"
   
   # On Windows
   ipconfig
   ```

### Backend URL Examples
```bash
# Local development
EXPO_PUBLIC_API_URL=http://192.168.1.100:8001

# Heroku production
EXPO_PUBLIC_API_URL=https://botmr-api-yourname.herokuapp.com

# Docker local
EXPO_PUBLIC_API_URL=http://localhost:8001
```

---

## 🐛 Troubleshooting

### Expo Go Issues

**"Network Error" or "Can't connect"**:
1. Make sure phone and computer are on same WiFi
2. Check firewall isn't blocking port 19000
3. Try restarting Metro bundler: `npm start -- --reset-cache`

**"Something went wrong"**:
1. Clear Expo Go cache: Settings → Clear Cache
2. Restart Expo Go app
3. Try `expo start --tunnel` for network issues

### Build Issues

**EAS Build Fails**:
```bash
# Check build logs
eas build:list

# View specific build
eas build:view [BUILD_ID]
```

**Android: "Could not download APK"**:
1. Check if build completed successfully
2. Try downloading on WiFi (not mobile data)
3. Enable "Install from Unknown Sources"

**iOS: "Untrusted Developer"**:
1. Go to Settings → General → VPN & Device Management
2. Trust the developer certificate
3. Try installing again

---

## 📊 Build Status Commands

```bash
# List all builds
eas build:list

# Check build status
eas build:view [BUILD_ID]

# Cancel running build
eas build:cancel [BUILD_ID]

# View build logs
eas build:view --json [BUILD_ID]
```

---

## 🎯 Recommended Workflow

### For Quick Testing
1. **Use Expo Go** - Instant testing, no builds needed
2. **Perfect for**: UI testing, basic functionality, development

### For Feature Testing
1. **Development Build** - Access to native features
2. **Perfect for**: Audio recording, push notifications, device APIs

### For Distribution
1. **Preview Build** - Share with testers
2. **Production Build** - App stores

---

## 📝 Important Notes

### Expo Go Limitations
- ❌ Cannot use custom native code
- ❌ Audio recording might be limited
- ✅ Perfect for UI and basic testing

### Development Builds
- ✅ Full native features (audio recording, etc.)
- ✅ Custom native modules
- ❌ Requires rebuilding for code changes

### Production Builds
- ✅ Optimized for app stores
- ✅ Smallest file size
- ✅ Best performance

---

## 🚨 Security Notes

1. **Never commit**:
   - API keys to Git
   - Production environment URLs
   - Build credentials

2. **Use environment variables** for all sensitive data

3. **Test on real devices** before production release

---

Your BotMR app is ready to test on real phones! 📱✨

**Quick Start**: Install Expo Go → `npm start` → Scan QR code → Done! 🎉