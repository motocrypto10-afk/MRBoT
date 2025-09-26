#!/bin/bash

# BotMR Deployment Script
# Usage: ./deploy.sh [local|heroku|build]

set -e

echo "🚀 BotMR Deployment Script"
echo "=========================="

case "${1:-help}" in
    "local")
        echo "📦 Starting Local Docker Deployment..."
        
        # Check if .env exists
        if [ ! -f .env ]; then
            echo "⚠️  Creating .env from template..."
            cp .env.example .env
            echo "❗ Please edit .env with your EMERGENT_LLM_KEY before continuing"
            echo "Press Enter when ready..."
            read
        fi
        
        # Start services
        echo "🐳 Starting Docker services..."
        docker-compose up -d
        
        # Wait for services
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        # Health check
        echo "🔍 Checking backend health..."
        curl -s http://localhost:8001/api/health | jq .status || echo "Backend not ready yet"
        
        echo "✅ Local deployment complete!"
        echo "📱 Frontend: http://localhost:3000"
        echo "🌐 Backend: http://localhost:8001/api/health"
        echo "🗄️  MongoDB: mongodb://localhost:27017"
        ;;
        
    "heroku")
        echo "☁️  Deploying to Heroku..."
        
        # Check if heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not installed. Install from: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        # Login check
        heroku whoami || {
            echo "🔑 Please login to Heroku first:"
            heroku login
        }
        
        # Get app name
        echo "Enter your Heroku app name (e.g., botmr-api-yourname):"
        read -r APP_NAME
        
        # Create app if needed
        heroku apps:info -a "$APP_NAME" || {
            echo "📱 Creating new Heroku app: $APP_NAME"
            heroku create "$APP_NAME"
        }
        
        # Set stack to container
        heroku stack:set container -a "$APP_NAME"
        
        # Add MongoDB addon
        heroku addons:info mongolab -a "$APP_NAME" || {
            echo "🗄️  Adding MongoDB addon..."
            heroku addons:create mongolab:sandbox -a "$APP_NAME"
        }
        
        # Set environment variables
        echo "Enter your EMERGENT_LLM_KEY:"
        read -r -s EMERGENT_LLM_KEY
        
        heroku config:set EMERGENT_LLM_KEY="$EMERGENT_LLM_KEY" -a "$APP_NAME"
        heroku config:set SECRET_KEY="$(openssl rand -base64 32)" -a "$APP_NAME"
        heroku config:set DEBUG=false -a "$APP_NAME"
        
        # Deploy
        echo "🚀 Deploying to Heroku..."
        git push heroku main
        
        # Open app
        heroku open -a "$APP_NAME"
        
        echo "✅ Heroku deployment complete!"
        echo "🌐 Your API: https://$APP_NAME.herokuapp.com/api/health"
        ;;
        
    "build")
        echo "📱 Building Mobile App..."
        
        cd frontend
        
        # Check if EAS is installed
        if ! command -v eas &> /dev/null; then
            echo "📥 Installing EAS CLI..."
            npm install -g @expo/eas-cli
        fi
        
        # Login to EAS
        eas whoami || {
            echo "🔑 Please login to EAS:"
            eas login
        }
        
        # Configure build
        eas build:configure || echo "Build already configured"
        
        echo "Which platform? (android/ios/both):"
        read -r PLATFORM
        
        case $PLATFORM in
            "android")
                echo "🤖 Building Android APK..."
                eas build --platform android --profile development
                ;;
            "ios")
                echo "🍎 Building iOS app..."
                eas build --platform ios --profile development
                ;;
            "both")
                echo "📱 Building for both platforms..."
                eas build --platform all --profile development
                ;;
            *)
                echo "❌ Invalid platform. Use: android, ios, or both"
                exit 1
                ;;
        esac
        
        echo "✅ Build started! Check status with: eas build:list"
        cd ..
        ;;
        
    "test")
        echo "🧪 Quick Health Check..."
        
        echo "Backend API:"
        curl -s http://localhost:8001/api/health | jq . || echo "❌ Backend not running"
        
        echo -e "\nFrontend:"
        curl -s http://localhost:3000 | grep -q "BotMR" && echo "✅ Frontend running" || echo "❌ Frontend not running"
        
        echo -e "\nMongoDB:"
        mongo --eval "db.adminCommand('ping')" --quiet && echo "✅ MongoDB running" || echo "❌ MongoDB not running"
        ;;
        
    *)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  local     Start local Docker development"
        echo "  heroku    Deploy to Heroku"
        echo "  build     Build mobile app with EAS"
        echo "  test      Run health checks"
        echo ""
        echo "Examples:"
        echo "  $0 local         # Start local development"
        echo "  $0 heroku        # Deploy to Heroku"
        echo "  $0 build android # Build Android APK"
        echo "  $0 test          # Check if services are running"
        ;;
esac