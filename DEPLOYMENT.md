# BotMR Deployment Guide

## 📋 Prerequisites

1. **GitHub Account** with your BotMR repository
2. **Heroku Account** (free tier available)
3. **Heroku CLI** installed locally
4. **Docker** installed for local development
5. **Emergent LLM Key** for AI functionality

## 🚀 Heroku Deployment from GitHub

### Step 1: Prepare Repository

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Create required environment files**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

### Step 2: Deploy to Heroku

#### Option A: Heroku Dashboard (Recommended)

1. Go to [Heroku Dashboard](https://dashboard.heroku.com)
2. Click **"New" → "Create new app"**
3. Choose app name (e.g., `botmr-api-yourname`)
4. Select region (US or Europe)
5. Go to **"Deploy"** tab
6. Select **"GitHub"** as deployment method
7. Connect your GitHub repository
8. Enable **"Automatic deploys"** from main branch
9. Click **"Deploy Branch"**

#### Option B: Heroku CLI

```bash
# Login to Heroku
heroku login

# Create new app
heroku create botmr-api-yourname

# Set stack to container (for Docker deployment)
heroku stack:set container -a botmr-api-yourname

# Add MongoDB addon
heroku addons:create mongolab:sandbox -a botmr-api-yourname

# Set environment variables
heroku config:set EMERGENT_LLM_KEY=your_key_here -a botmr-api-yourname
heroku config:set SECRET_KEY=your_secret_key_here -a botmr-api-yourname

# Deploy
git push heroku main
```

### Step 3: Configure Environment Variables

In Heroku Dashboard → Settings → Config Vars, add:

```
EMERGENT_LLM_KEY=your_emergent_llm_key_here
SECRET_KEY=your_secret_key_change_in_production
MONGO_URL=your_mongodb_connection_string
DB_NAME=emergent
DEBUG=false
```

### Step 4: Verify Deployment

1. Open your app: `https://your-app-name.herokuapp.com/api/health`
2. Check logs: `heroku logs --tail -a your-app-name`

## 🐳 Local Docker Development

### Quick Start

1. **Clone and setup**:
   ```bash
   git clone your-repo-url
   cd botmr
   cp .env.example .env
   # Edit .env with your values
   ```

2. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Check services**:
   ```bash
   docker-compose ps
   curl http://localhost:8001/api/health
   ```

### Individual Service Commands

```bash
# Start only database
docker-compose up -d mongodb redis

# Build and start backend
docker-compose up --build backend

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Reset database
docker-compose down -v
docker-compose up -d
```

## 📱 Mobile App Testing

### Option 1: Expo Go (Recommended for Testing)

1. **Install Expo Go** on your phone:
   - [iOS App Store](https://apps.apple.com/app/expo-go/id982107779)
   - [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. **Start development server**:
   ```bash
   cd frontend
   npm start
   # or
   yarn start
   ```

3. **Scan QR code** with Expo Go app or camera

### Option 2: Development Build (More Native Features)

1. **Install EAS CLI**:
   ```bash
   npm install -g @expo/eas-cli
   ```

2. **Configure EAS**:
   ```bash
   cd frontend
   eas login
   eas build:configure
   ```

3. **Build for device**:
   ```bash
   # For Android APK
   eas build --platform android --profile development

   # For iOS (requires Apple Developer Account)
   eas build --platform ios --profile development
   ```

4. **Install on device** using the download link from EAS

### Option 3: Production Build

```bash
# Android APK
eas build --platform android --profile production

# iOS App Store
eas build --platform ios --profile production

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

## 🔧 Environment Configuration

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017/emergent` |
| `EMERGENT_LLM_KEY` | AI service key | `your_key_here` |
| `SECRET_KEY` | App secret for security | `your_secret_key` |
| `DEBUG` | Debug mode | `false` |
| `PORT` | Server port (Heroku sets this) | `8001` |

### Frontend Environment Variables

Create `frontend/.env`:
```
EXPO_PUBLIC_API_URL=https://your-app.herokuapp.com
```

## 🚨 Troubleshooting

### Common Deployment Issues

1. **Build Fails**:
   ```bash
   # Check Heroku logs
   heroku logs --tail
   
   # Restart dynos
   heroku restart
   ```

2. **Database Connection Issues**:
   ```bash
   # Verify MongoDB addon
   heroku addons
   
   # Check config vars
   heroku config
   ```

3. **App Won't Start**:
   ```bash
   # Scale dynos
   heroku ps:scale web=1
   
   # Check processes
   heroku ps
   ```

### Local Development Issues

1. **Port Conflicts**:
   ```bash
   # Stop other services using ports
   sudo lsof -ti:8001 | xargs kill -9
   sudo lsof -ti:27017 | xargs kill -9
   ```

2. **Docker Issues**:
   ```bash
   # Reset Docker
   docker-compose down -v
   docker system prune -a
   docker-compose up --build
   ```

## 📚 Additional Resources

- [Heroku Container Registry](https://devcenter.heroku.com/articles/container-registry-and-runtime)
- [Expo Development Builds](https://docs.expo.dev/development/build/)
- [MongoDB Atlas](https://www.mongodb.com/atlas) for production database
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🔐 Security Considerations

1. **Never commit secrets** to Git
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** in production
4. **Rotate secrets regularly**
5. **Monitor access logs**

Your BotMR app is now ready for deployment! 🎉