# 🚀 Google Drive Transfer Pro - Full-Stack Application

A modern, full-featured web application for managing and transferring files with Google Drive. Built with React + Vite frontend and Flask backend.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-lightgrey)

## ✨ Features

### 🔐 Authentication & Security
- Secure username/password authentication
- Session management
- CORS protection
- Input validation

### 📁 File Management
- **List All Files** - Browse all your Google Drive files
- **Real-time Updates** - File list updates automatically
- **Search Files** - Search through your files
- **Delete Files** - Remove unwanted files
- **File Selection** - Select single or multiple files

### 🔄 Transfer Capabilities
- **Drive Link Transfer** - Copy files from shared Google Drive links to your drive
- **Direct URL Upload** - Upload files from Seedr, Mega, MediaFire, Dropbox, and other platforms
- **Server-to-Server** - No download/upload needed for Drive transfers
- **Large File Support** - Handle files up to 30GB

### 📊 Progress Tracking
- **Real-time Progress** - See extraction/upload progress with 2-second updates
- **Active Tasks Panel** - Monitor all ongoing operations
- **Progress Bars** - Visual feedback for all operations
- **Status Notifications** - Success/error messages

### 🎨 Modern UI
- Beautiful gradient design
- Responsive layout (mobile & desktop)
- File type icons
- Loading animations
- Error handling

## 🏗️ Architecture

```
google-drive-transfer-app/
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── api/            # API client
│   │   ├── store/          # Zustand state management
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json
│   └── vite.config.js
├── app_new.py              # Flask backend (updated)
├── app.py                  # Original Flask app (legacy)
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Google OAuth credentials
- npm or yarn

### Step 1: Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd google-drive-transfer-app

# Run setup script (Linux/Mac)
chmod +x setup.sh
./setup.sh

# Or setup manually:
# 1. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Configure Environment

Create `.env` file in root directory:

```env
# Google OAuth Credentials
CLIENT_ID=your-google-oauth-client-id
CLIENT_SECRET=your-google-oauth-client-secret
REDIRECT_URI=http://localhost:3000/oauth2callback
REFRESH_TOKEN=your-google-oauth-refresh-token

# Authentication
AUTH_USERNAME=admin
AUTH_PASSWORD=secure123

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Server Configuration
PORT=5000
```

### Step 3: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:3000/oauth2callback`
6. Download credentials and get refresh token
7. Update `.env` file with your credentials

### Step 4: Run the Application

Open two terminals:

**Terminal 1 - Backend:**
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app_new.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit: **http://localhost:3000**

## 🎯 Usage

### 1. Login
- Default credentials: `admin` / `secure123`
- Change in `.env` file: `AUTH_USERNAME` and `AUTH_PASSWORD`

### 2. Transfer from Google Drive Link
- Paste a shared Google Drive URL
- Optionally provide a custom filename
- Click "Transfer to My Drive"
- File is copied server-to-server (no download needed!)

### 3. Upload from Direct URL
- Paste a direct download link (Seedr, Mega, etc.)
- Optionally provide a filename
- Click "Upload to My Drive"
- File downloads to server, then uploads to Drive

### 4. Browse & Manage Files
- View all your Google Drive files
- See file size, type, and modification date
- Select files for batch operations
- Extract/download files with progress tracking
- Delete unwanted files

### 5. Monitor Progress
- Active Tasks panel shows all ongoing operations
- Progress updates every 2 seconds
- Visual progress bars for extraction/upload
- Success/failure notifications

## 📡 API Endpoints

### Authentication
- `POST /api/login` - Login
- `POST /api/logout` - Logout
- `GET /api/auth/check` - Check auth status

### Files
- `GET /api/files/list` - List all files
- `GET /api/files/:id/metadata` - Get file metadata
- `POST /api/files/extract` - Extract/download file
- `DELETE /api/files/:id` - Delete file
- `GET /api/files/search?q=query` - Search files

### Transfers
- `POST /api/transfer` - Transfer from Drive link
- `POST /api/files/upload-from-url` - Upload from URL
- `GET /api/files/progress/:taskId` - Get task progress

### Health
- `GET /api/health` - Health check

## 🛡️ Security Features

- ✅ Session-based authentication
- ✅ CORS protection
- ✅ Input validation
- ✅ File size limits (30GB max)
- ✅ Secure token management
- ✅ Environment variable configuration
- ✅ Error handling
- ✅ Request timeout protection

## 🎨 Tech Stack

### Frontend
- **React 18** - UI library
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Axios** - HTTP client
- **Lucide React** - Icons

### Backend
- **Flask** - Web framework
- **Flask-CORS** - CORS handling
- **Requests** - HTTP client
- **Python 3.11** - Programming language

## 📦 Deployment

### Build for Production

```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/dist/
# Flask will serve these files in production
```

### Deploy Options

1. **Railway** - Recommended
2. **Render** - Free tier available
3. **Vercel** - Frontend only
4. **Heroku** - Limited free tier
5. **DigitalOcean** - VPS hosting

### Production Environment Variables

Set these in your hosting platform:

```env
CLIENT_ID=your-production-client-id
CLIENT_SECRET=your-production-client-secret
REDIRECT_URI=https://your-domain.com/oauth2callback
REFRESH_TOKEN=your-production-refresh-token
AUTH_USERNAME=admin
AUTH_PASSWORD=your-secure-password
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
```

## 🐛 Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend errors
```bash
# Check Python version
python3 --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check .env file exists and has correct values
cat .env
```

### CORS errors
- Ensure backend is running on port 5000
- Frontend is running on port 3000
- CORS is configured in app_new.py

### OAuth errors
- Verify credentials in .env
- Check redirect URI matches Google Console
- Ensure Google Drive API is enabled
- Refresh token may have expired

## 📝 Development

### Code Structure

**Frontend Components:**
- `Login.jsx` - Authentication page
- `Header.jsx` - Top navigation bar
- `TransferPanel.jsx` - Drive link transfer
- `URLUploadPanel.jsx` - Direct URL upload
- `FileList.jsx` - File browser
- `ActiveTasks.jsx` - Progress monitor

**Backend Routes:**
- Authentication routes
- File management routes
- Transfer routes
- Progress tracking routes

### Adding New Features

1. Create component in `frontend/src/components/`
2. Add API endpoint in `app_new.py`
3. Update API client in `frontend/src/api/client.js`
4. Add state management in `frontend/src/store/useStore.js`
5. Test thoroughly

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Google Drive API
- React & Vite communities
- Flask community
- All contributors

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🔄 Version History

### Version 2.0.0 (Current)
- ✅ Full Vite + React frontend
- ✅ File listing and browsing
- ✅ Real-time progress tracking (2-second updates)
- ✅ Direct URL upload support
- ✅ File extraction capability
- ✅ Modern UI with Tailwind CSS
- ✅ Enhanced security features

### Version 1.0.0
- Basic Flask application
- Simple HTML templates
- Drive link transfer only

---

**Made with ❤️ using React, Vite, and Flask**
