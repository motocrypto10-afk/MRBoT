# 🚀 BotMR Quick Deployment & Testing Guide

## 📱 IMMEDIATE TESTING ON REAL PHONE (2 minutes)

### Step 1: Install Expo Go
- **iPhone**: [App Store - Expo Go](https://apps.apple.com/app/expo-go/id982107779)
- **Android**: [Google Play - Expo Go](https://play.google.com/store/apps/details?id=host.exp.exponent)

### Step 2: Get QR Code
Your app is already running! 

1. **Open in browser**: http://localhost:3000
2. **Scan QR code** with Expo Go app
3. **Done!** App loads on your phone in 30 seconds

**Alternative URLs to try**:
- http://127.0.0.1:3000 
- Check your current tunnel URL in the browser

---

## 🌐 HEROKU DEPLOYMENT (10 minutes)

### Option A: GitHub → Heroku (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Deploy on Heroku**:
   - Go to [dashboard.heroku.com](https://dashboard.heroku.com)
   - Create New App → Connect GitHub → Enable Auto Deploy
   - Add Config Vars:
     ```
     EMERGENT_LLM_KEY=your_key_here
     SECRET_KEY=your_secret_key
     ```

3. **Your API will be live at**: `https://your-app-name.herokuapp.com/api/health`

### Option B: Heroku CLI
```bash
# Install Heroku CLI, then:
heroku login
heroku create botmr-api-yourname
heroku stack:set container
heroku config:set EMERGENT_LLM_KEY=your_key_here
git push heroku main
```

---

## 🐳 DOCKER LOCAL DEPLOYMENT (5 minutes)

### Quick Start
```bash
# Copy environment file
cp .env.example .env
# Edit .env with your EMERGENT_LLM_KEY

# Start all services
docker-compose up -d

# Check health
curl http://localhost:8001/api/health
```

### Individual Commands
```bash
# Start only backend + database
docker-compose up -d mongodb redis backend

# View logs
docker-compose logs -f backend

# Stop all
docker-compose down
```

---

## 📲 MOBILE APP BUILDS

### For Quick Testing: Use Expo Go (Already working above!)

### For Advanced Features: Development Build
```bash
# Install EAS CLI
npm install -g @expo/eas-cli

cd frontend
eas login
eas build:configure

# Build Android APK (no account needed)
eas build --platform android --profile development

# Build iOS (requires Apple Developer Account)
eas build --platform ios --profile development
```

---

## ⚙️ CONFIGURATION

### Backend Environment (.env)
```bash
MONGO_URL=mongodb://localhost:27017/emergent
EMERGENT_LLM_KEY=your_emergent_llm_key_here
SECRET_KEY=your_secret_key
DEBUG=false
```

### Frontend Environment (frontend/.env)
```bash
# For local testing
EXPO_PUBLIC_API_URL=http://localhost:8001

# For Heroku deployment  
EXPO_PUBLIC_API_URL=https://your-app-name.herokuapp.com
```

---

## 🔍 TESTING CHECKLIST

### Backend API Testing
```bash
# Health check
curl http://localhost:8001/api/health

# Get meetings
curl http://localhost:8001/api/meetings

# Test recording
curl -X POST http://localhost:8001/api/recordings/start \
  -H "Content-Type: application/json" \
  -d '{"mode":"local","metadata":{"deviceId":"test"}}'
```

### Mobile App Testing
1. **✅ Navigation**: Bottom tabs work
2. **✅ UI**: Apple-style interface loads
3. **✅ API**: Meeting data loads
4. **✅ Recording**: Start/stop recording works
5. **✅ Network**: Works on different WiFi networks

---

## 🚨 TROUBLESHOOTING

### "Network Error" on Phone
1. **Same WiFi**: Phone and computer on same network
2. **Firewall**: Disable firewall temporarily
3. **IP Address**: Use computer's IP instead of localhost
   ```bash
   # Find your IP
   ifconfig | grep "inet 192"  # Mac/Linux
   ipconfig                    # Windows
   ```

### Heroku Deployment Fails
```bash
# Check logs
heroku logs --tail -a your-app-name

# Restart app
heroku restart -a your-app-name

# Check config
heroku config -a your-app-name
```

### Docker Issues
```bash
# Reset everything
docker-compose down -v
docker system prune -a
docker-compose up --build
```

---

## 📋 PRODUCTION CHECKLIST

### Before Going Live
- [ ] Set `DEBUG=false` in backend .env
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production MongoDB (MongoDB Atlas)
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS properly
- [ ] Test on multiple devices
- [ ] Set up monitoring/logging

### App Store Deployment
```bash
# Production builds
eas build --platform android --profile production
eas build --platform ios --profile production

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

---

## 🎯 RECOMMENDED WORKFLOW

### Development
1. **Local**: Use Docker Compose for backend
2. **Testing**: Use Expo Go for instant mobile testing
3. **Features**: Use development builds for native features

### Staging
1. **Deploy**: Use Heroku for staging API
2. **Test**: Use preview builds for team testing

### Production
1. **Deploy**: Use production Heroku or cloud provider
2. **Distribute**: Use app stores or enterprise distribution

---

## 📞 QUICK SUPPORT

### Most Common Issues
1. **"Can't connect to server"** → Check EXPO_PUBLIC_API_URL in frontend/.env
2. **"Module not found"** → Run `npm install` in frontend/
3. **"Database error"** → Check MONGO_URL in backend/.env
4. **"Build fails"** → Check EAS build logs with `eas build:list`

### Your Current Setup
- **Backend**: Running on http://localhost:8001
- **Frontend**: Running on http://localhost:3000  
- **Mobile**: Scan QR code from http://localhost:3000
- **Database**: MongoDB running locally

---

**🎉 Your BotMR app is ready to deploy and test!**

**Quick Start**: Scan QR code → Install on phone → Start recording meetings! 📱✨