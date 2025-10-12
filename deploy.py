#!/usr/bin/env python3
"""
Quick deployment script for Google Drive Transfer App
Helps you deploy to various free platforms
"""

import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

PLATFORMS = {
    "railway": {
        "name": "Railway",
        "url": "https://railway.app",
        "instructions": [
            "1. Go to https://railway.app",
            "2. Sign up with GitHub",
            "3. Create New Project > Deploy from GitHub repo",
            "4. Select this repository",
            "5. Add environment variables in Settings",
            "6. Deploy automatically!"
        ],
        "env_vars": True,
        "free_tier": "500 hours/month",
        "pros": ["Always free tier", "Easy setup", "Auto HTTPS", "Custom domains"],
        "cons": ["500 hour monthly limit"]
    },
    "render": {
        "name": "Render",
        "url": "https://render.com",
        "instructions": [
            "1. Go to https://render.com",
            "2. Sign up with GitHub",
            "3. Create New > Web Service",
            "4. Connect this repository",
            "5. Set environment variables",
            "6. Deploy!"
        ],
        "env_vars": True,
        "free_tier": "750 hours/month",
        "pros": ["Free tier", "Auto HTTPS", "Easy Git integration"],
        "cons": ["Sleeps after 15min inactivity", "750 hour limit"]
    },
    "vercel": {
        "name": "Vercel",
        "url": "https://vercel.com",
        "instructions": [
            "1. Go to https://vercel.com",
            "2. Sign up with GitHub",
            "3. Import Project from GitHub",
            "4. Select this repository",
            "5. Add environment variables",
            "6. Deploy!"
        ],
        "env_vars": True,
        "free_tier": "Good limits",
        "pros": ["Fast edge deployment", "Great free tier", "Instant deploys"],
        "cons": ["10 second timeout limit for functions"]
    },
    "heroku": {
        "name": "Heroku",
        "url": "https://heroku.com",
        "instructions": [
            "1. Go to https://heroku.com",
            "2. Create account",
            "3. Create new app",
            "4. Connect to GitHub repo",
            "5. Add Config Vars (environment variables)",
            "6. Deploy from GitHub branch"
        ],
        "env_vars": True,
        "free_tier": "Limited (550 hours/month)",
        "pros": ["Well-known platform", "Good documentation"],
        "cons": ["Limited free tier", "Sleeps after 30min"]
    },
    "pythonanywhere": {
        "name": "PythonAnywhere",
        "url": "https://www.pythonanywhere.com",
        "instructions": [
            "1. Go to https://www.pythonanywhere.com",
            "2. Create free account",
            "3. Upload your code files",
            "4. Create a web app",
            "5. Configure WSGI file",
            "6. Set environment variables"
        ],
        "env_vars": True,
        "free_tier": "1 web app",
        "pros": ["Always-on free tier", "Python-focused", "Good for beginners"],
        "cons": ["Limited to 1 app", "Custom domain requires paid plan"]
    }
}

ENV_VARS = {
    "CLIENT_ID": "your-google-oauth-client-id",
    "CLIENT_SECRET": "your-google-oauth-client-secret",
    "REFRESH_TOKEN": "your-google-oauth-refresh-token",
    "AUTH_USERNAME": "admin",
    "AUTH_PASSWORD": "secure123",
    "SECRET_KEY": "your-random-secret-key-here",
    "FLASK_ENV": "production"
}

def print_header():
    print("🚀 Google Drive Transfer App - Deployment Helper")
    print("=" * 60)
    print("Choose your deployment platform and get step-by-step instructions!")
    print()

def list_platforms():
    print("📋 Available Free Platforms:")
    print()
    for i, (key, platform) in enumerate(PLATFORMS.items(), 1):
        print(f"{i}. {platform['name']}")
        print(f"   Free Tier: {platform['free_tier']}")
        print(f"   Pros: {', '.join(platform['pros'])}")
        print(f"   Cons: {', '.join(platform['cons'])}")
        print()

def show_platform_instructions(platform_key):
    platform = PLATFORMS[platform_key]
    print(f"🎯 Deploying to {platform['name']}")
    print("=" * 40)
    print()
    
    print("📝 Step-by-step Instructions:")
    for instruction in platform['instructions']:
        print(f"   {instruction}")
    print()
    
    if platform['env_vars']:
        print("🔧 Environment Variables to Set:")
        print("Copy these exact values:")
        print()
        for key, value in ENV_VARS.items():
            if key == "SECRET_KEY":
                print(f"   {key} = {generate_secret_key()}")
            elif key in ["AUTH_USERNAME", "AUTH_PASSWORD"]:
                print(f"   {key} = {value}  # ⚠️ CHANGE THIS!")
            else:
                print(f"   {key} = {value}")
        print()
    
    print("🌐 Ready to deploy?")
    choice = input(f"Open {platform['name']} website? (y/N): ").lower().strip()
    if choice == 'y':
        webbrowser.open(platform['url'])

def generate_secret_key():
    """Generate a random secret key"""
    import secrets
    return secrets.token_hex(32)

def create_deployment_checklist():
    """Create a deployment checklist file"""
    checklist = """
# 🚀 Deployment Checklist

## Pre-Deployment
- [ ] Code is working locally
- [ ] All files are committed to Git
- [ ] Repository is public on GitHub
- [ ] Environment variables are prepared

## Environment Variables
```
CLIENT_ID=your-google-oauth-client-id
CLIENT_SECRET=your-google-oauth-client-secret
REFRESH_TOKEN=your-google-oauth-refresh-token
AUTH_USERNAME=admin  # ⚠️ CHANGE THIS!
AUTH_PASSWORD=secure123  # ⚠️ CHANGE THIS!
SECRET_KEY=your-random-secret-key
FLASK_ENV=production
```

## Post-Deployment
- [ ] App loads successfully
- [ ] Login works with your credentials
- [ ] File transfer works with test file
- [ ] HTTPS is enabled
- [ ] Custom domain configured (optional)

## Test File
Use this URL for testing:
https://drive.google.com/file/d/1kKoD6alsXMGIyGL656vF4xmDuUJB3-uY/view?usp=drivesdk

## Security
- [ ] Changed default username/password
- [ ] Generated new secret key
- [ ] Verified environment variables are secure
"""
    
    with open("DEPLOYMENT_CHECKLIST.md", "w") as f:
        f.write(checklist)
    print("✅ Created DEPLOYMENT_CHECKLIST.md")

def main():
    print_header()
    
    while True:
        list_platforms()
        
        try:
            choice = input("Enter platform number (1-5) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                break
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(PLATFORMS):
                platform_key = list(PLATFORMS.keys())[choice_num - 1]
                show_platform_instructions(platform_key)
                
                create_checklist = input("\nCreate deployment checklist file? (y/N): ").lower().strip()
                if create_checklist == 'y':
                    create_deployment_checklist()
                
                print("\n" + "="*60 + "\n")
            else:
                print("❌ Invalid choice. Please try again.\n")
                
        except ValueError:
            print("❌ Invalid input. Please enter a number.\n")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()