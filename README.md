# 🚀 Google Drive Transfer - Python Flask App

A secure web application for transferring files from shared Google Drive links to your personal Google Drive. This is a Python Flask version of the Cloudflare Worker with the same exact functionality and UI.

![Google Drive Transfer](https://img.shields.io/badge/Google%20Drive-Transfer-blue?style=for-the-badge&logo=googledrive)
![Python](https://img.shields.io/badge/Python-3.11-green?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3-lightgrey?style=for-the-badge&logo=flask)

## ✨ Features

- 🔐 **Secure Authentication** - Simple username/password protection
- 🎯 **Direct Server-to-Server Transfer** - No download/upload, just copy
- 📊 **Real-time Progress** - Beautiful UI with transfer status
- 💾 **Large File Support** - Handles files up to 10GB
- 🌐 **Free Deployment** - Deploy on Railway, Render, Vercel, or other platforms
- 🔄 **Automatic Token Refresh** - Handles OAuth token expiration

## 🚀 Quick Deploy

### Option 1: Railway (Recommended - Always Free)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/python-flask)

1. Click the Railway button above
2. Connect your GitHub account
3. Fork this repository
4. Set environment variables (see below)
5. Deploy! 🎉

### Option 2: Render (Free tier available)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

1. Go to [Render.com](https://render.com)
2. Create a new Web Service
3. Connect this repository
4. Set environment variables
5. Deploy!

### Option 3: Vercel (Free tier available)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Click the Vercel button above
2. Import this repository
3. Set environment variables
4. Deploy!

### Option 4: Heroku (Has free tier limitations)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

1. Click the Heroku button above
2. Set environment variables
3. Deploy!

## 🔧 Environment Variables

**⚠️ Important: You need to set up your own Google OAuth credentials!**

👉 **[Follow the complete setup guide](SETUP.md)** to get your credentials.

Set these environment variables in your deployment platform:

| Variable | Example Value | Description |
|----------|-------|-------------|
| `CLIENT_ID` | `your-google-oauth-client-id` | Google OAuth Client ID |
| `CLIENT_SECRET` | `your-google-oauth-client-secret` | Google OAuth Client Secret |
| `REFRESH_TOKEN` | `your-google-oauth-refresh-token` | Your Google OAuth Refresh Token |
| `AUTH_USERNAME` | `admin` | App login username (change this!) |
| `AUTH_PASSWORD` | `secure123` | App login password (change this!) |
| `SECRET_KEY` | `random-secret-key` | Flask session secret (generate random) |
| `FLASK_ENV` | `production` | Flask environment |
| `PORT` | `5000` | Server port (auto-set by platforms) |

## 🏃‍♂️ Local Development

### Prerequisites

- Python 3.11+
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd google-drive-transfer-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   ```
   http://localhost:5000
   ```

## 📋 How to Use

1. **Login** with your configured username/password
2. **Paste Google Drive URL** (shared link)
3. **Optional:** Set custom filename
4. **Click Transfer** and wait for completion
5. **Success!** File is now in your Google Drive

### Supported URL Formats

- `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
- `https://drive.google.com/file/d/FILE_ID/view?usp=drivesdk`
- `https://drive.google.com/open?id=FILE_ID`

## 🔐 Getting Your Refresh Token

**👉 [Complete setup guide available here](SETUP.md)**

Quick script for getting credentials:

```python
# Quick token generator - see SETUP.md for full instructions
import webbrowser
import requests

CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"

# Full instructions in SETUP.md
```

## 🆚 Comparison with Cloudflare Worker

| Feature | Python Flask | Cloudflare Worker |
|---------|-------------|-------------------|
| **Memory Limit** | Unlimited | Limited |
| **File Size** | Up to 10GB+ | Up to 10GB |
| **Deployment Cost** | Free (many platforms) | Free |
| **Cold Start** | ~2-3 seconds | ~100ms |
| **Scalability** | Platform dependent | Auto-scaling |
| **Maintenance** | Platform handles | Minimal |

## 🛠️ Deployment Platform Details

### Railway
- ✅ **Always free tier** (500 hours/month)
- ✅ **Easy deployment**
- ✅ **Automatic HTTPS**
- ✅ **Custom domains**
- ⚠️ **500 hours/month limit**

### Render
- ✅ **Free tier available**
- ✅ **Automatic HTTPS**
- ✅ **Auto-deploy from Git**
- ⚠️ **Sleeps after 15 min inactivity**
- ⚠️ **750 hours/month limit**

### Vercel
- ✅ **Generous free tier**
- ✅ **Edge locations**
- ✅ **Fast deployments**
- ⚠️ **10-second timeout limit**

### Fly.io
- ✅ **Free allowance**
- ✅ **Global deployment**
- ✅ **No sleep**
- ⚠️ **Usage-based pricing**

## 🔒 Security Features

- **Session-based authentication**
- **Environment variable protection**
- **HTTPS enforcement on platforms**
- **Token refresh automation**
- **Input validation**
- **CSRF protection**

## 🎛️ Configuration

### File Size Limits
```python
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
CHUNK_SIZE = 100 * 1024 * 1024  # 100MB chunks
```

### Authentication
```python
AUTH_USERNAME = 'your-username'
AUTH_PASSWORD = 'your-secure-password'
```

## 🐛 Troubleshooting

### Common Issues

1. **404 File Not Found**
   - Ensure file is publicly accessible
   - Check if file ID is correct
   - Try with `supportsAllDrives=true`

2. **Token Expired**
   - App automatically refreshes tokens
   - Check refresh token validity
   - Regenerate tokens if needed

3. **File Too Large**
   - Maximum 10GB per file
   - Use server-to-server copy (no memory limits)

4. **Deployment Issues**
   - Check environment variables
   - Verify Python version (3.11+)
   - Check platform-specific logs

### Debug Mode

For local development:
```bash
export FLASK_ENV=development
python app.py
```

## 📊 Performance

- **Transfer Speed**: Direct Google server-to-server copy
- **Memory Usage**: Minimal (no file buffering)
- **Concurrent Users**: Platform dependent
- **File Size**: Up to 10GB+ (no memory limits)

## 🔄 Updates

The app automatically handles:
- ✅ Token refresh
- ✅ Error handling
- ✅ File size validation
- ✅ URL parsing
- ✅ Progress tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section
2. Review deployment platform logs
3. Verify environment variables
4. Test with smaller files first

## 🎉 Success!

Once deployed, you'll have a secure, fast, and reliable Google Drive file transfer service running on your chosen platform! 

**Live Example**: Your app will look exactly like the Cloudflare Worker but with Python reliability and unlimited memory for large files.

---

Made with ❤️ for seamless Google Drive file transfers