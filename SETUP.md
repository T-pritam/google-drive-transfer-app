# 🔧 Setup Guide - Getting Your Google OAuth Credentials

This guide will help you set up your own Google OAuth credentials for the Google Drive Transfer app.

## 📋 Prerequisites

- Google account
- Access to Google Cloud Console

## 🚀 Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `drive-transfer-app`
4. Click **"Create"**

## 🔧 Step 2: Enable Google Drive API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Drive API"**
3. Click on it and press **"Enable"**

## 🔐 Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth 2.0 Client IDs"**
3. If prompted, configure OAuth consent screen first:
   - Choose **"External"** user type
   - Fill in app name: `Drive Transfer App`
   - Add your email in required fields
   - Add scopes: `../auth/drive`
   - Save and continue

4. For OAuth Client ID:
   - Application type: **"Web application"**
   - Name: `Drive Transfer Client`
   - Authorized redirect URIs: `http://localhost:3000/oauth2callback`
   - Click **"Create"**

5. **Copy the Client ID and Client Secret** - you'll need these!

## 🎯 Step 4: Get Refresh Token

Create a file called `get-token.py` and run it:

```python
#!/usr/bin/env python3
import webbrowser
import requests

# Replace with your actual credentials from Step 3
CLIENT_ID = "your-client-id-here"
CLIENT_SECRET = "your-client-secret-here"

print("🔑 Getting Google OAuth Refresh Token")
print("="*50)

# Step 1: Authorization URL
auth_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth?"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri=http://localhost:3000/oauth2callback&"
    f"scope=https://www.googleapis.com/auth/drive&"
    f"response_type=code&"
    f"access_type=offline&"
    f"prompt=consent"
)

print("1. Opening browser for authorization...")
print("2. Grant permission to access Google Drive")
print("3. Copy the authorization code from the URL")
print()

webbrowser.open(auth_url)

# Step 2: Get authorization code
auth_code = input("Enter authorization code: ").strip()

if not auth_code:
    print("❌ No authorization code provided")
    exit(1)

# Step 3: Exchange for tokens
print("\n🔄 Exchanging code for tokens...")

response = requests.post('https://oauth2.googleapis.com/token', data={
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'code': auth_code,
    'grant_type': 'authorization_code',
    'redirect_uri': 'http://localhost:3000/oauth2callback'
})

if response.status_code == 200:
    tokens = response.json()
    print("\n✅ SUCCESS! Your credentials:")
    print(f"CLIENT_ID={CLIENT_ID}")
    print(f"CLIENT_SECRET={CLIENT_SECRET}")
    print(f"REFRESH_TOKEN={tokens['refresh_token']}")
    print("\n📝 Copy these to your .env file or deployment environment variables!")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
```

## 🌐 Step 5: Configure Your App

### For Local Development:
1. Copy `.env.example` to `.env`
2. Replace placeholder values with your actual credentials:
   ```
   CLIENT_ID=your-actual-client-id
   CLIENT_SECRET=your-actual-client-secret
   REFRESH_TOKEN=your-actual-refresh-token
   AUTH_USERNAME=your-username
   AUTH_PASSWORD=your-secure-password
   SECRET_KEY=your-random-secret-key
   ```

### For Deployment:
Set these environment variables in your deployment platform:
- `CLIENT_ID`
- `CLIENT_SECRET`
- `REFRESH_TOKEN`
- `AUTH_USERNAME`
- `AUTH_PASSWORD`
- `SECRET_KEY`

## 🔒 Security Best Practices

1. **Never commit credentials to Git**
2. **Use environment variables** for all sensitive data
3. **Change default username/password**
4. **Generate a random secret key**
5. **Keep refresh token secure**

## ✅ Test Your Setup

1. Run the app locally: `python app.py`
2. Login with your credentials
3. Test with a small Google Drive file
4. Verify the transfer works

## 🆘 Troubleshooting

### Common Issues:

**"Invalid client" error:**
- Check CLIENT_ID and CLIENT_SECRET are correct
- Verify redirect URI matches exactly

**"Invalid grant" error:**
- Refresh token may be expired
- Re-run the get-token.py script

**"Access denied" error:**
- Check Google Drive API is enabled
- Verify OAuth consent screen is configured

**"File not found" error:**
- Ensure file is publicly accessible
- Check file ID in URL is correct

## 🎉 You're Ready!

Once you have all credentials configured, your app will be able to:
- ✅ Authenticate with Google Drive
- ✅ Access shared files
- ✅ Transfer files to your personal Drive
- ✅ Handle large files (5GB+)

---

Need help? Check the main README.md for deployment instructions!