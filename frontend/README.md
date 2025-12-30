# 🚀 Google Drive Transfer Pro - Pure Vite App

A **100% client-side** Google Drive file manager built with Vite + React. No backend required!

## ✨ Features

- ✅ **Pure Client-Side** - Runs entirely in your browser
- ✅ **Google Drive Integration** - Direct API access
- ✅ **File Management** - List, view, download, delete files
- ✅ **File Transfer** - Copy files from shared Drive links
- ✅ **No Backend** - Deploy anywhere as static files
- ✅ **Secure** - OAuth 2.0 authentication
- ✅ **Fast** - Vite powered development

## 🚀 Quick Start

### 1. Setup Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Drive API**
4. Go to **Credentials** → Create **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Add authorized JavaScript origins:
   - `http://localhost:5173` (development)
   - Your production domain
7. Copy the **Client ID**

### 2. Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

### 3. Install & Run

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Visit: **http://localhost:5173**

## 📦 Deployment

Deploy the `dist/` folder to any static hosting:

### Vercel
```bash
npm run build
npx vercel --prod
```

### Netlify
```bash
npm run build
# Drag & drop dist/ folder to Netlify
```

### GitHub Pages
```bash
npm run build
# Push dist/ to gh-pages branch
```

### Firebase Hosting
```bash
npm run build
firebase deploy
```

## 🔐 Security

- ✅ All operations happen in your browser
- ✅ OAuth 2.0 with PKCE flow
- ✅ No data sent to external servers
- ✅ Your files stay in Google Drive
- ✅ Access token stored in localStorage

## ⚠️ Limitations

Since this is a pure client-side app:

- ❌ **No URL uploads** - Cannot download from Seedr/Mega/etc to Drive (requires backend)
- ✅ **File transfers work** - Copy files from shared Drive links
- ✅ **File downloads work** - Download files to your computer
- ✅ **File management works** - List, delete, view files

## 🛠️ Tech Stack

- **React 18** - UI library
- **Vite 5** - Build tool
- **Tailwind CSS 3** - Styling
- **Zustand** - State management
- **Google Drive API** - Direct integration
- **Google Identity Services** - OAuth

## 📚 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_GOOGLE_CLIENT_ID` | Yes | Your Google OAuth Client ID |
| `VITE_GOOGLE_API_KEY` | No | Google API Key (optional) |

## 🎯 Usage

1. **Login** - Click "Sign in with Google"
2. **Grant Permissions** - Allow access to Google Drive
3. **Browse Files** - See all your Drive files
4. **Transfer Files** - Copy from shared Drive links
5. **Download Files** - Extract files to your computer
6. **Delete Files** - Remove unwanted files

## 🔧 Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production
npm run preview

# Lint code
npm run lint
```

## 🌐 Production Build

The production build is optimized and ready for deployment:

```bash
npm run build
# Output: dist/
```

Deploy the `dist/` folder to any static hosting service.

## ❓ FAQ

**Q: Why no backend?**  
A: This is a pure client-side app for maximum simplicity and deployability.

**Q: Is my data safe?**  
A: Yes! Everything runs in your browser. No external servers involved.

**Q: Can I upload from URLs?**  
A: No, that requires a backend. But you can copy from Drive links and download files.

**Q: Where is the access token stored?**  
A: In your browser's localStorage. Clear it to logout completely.

**Q: Can I use this with G Suite/Workspace?**  
A: Yes! Just use your organization's Google account.

## 📄 License

MIT License

## 🙏 Credits

Built with ❤️ using:
- React
- Vite
- Tailwind CSS
- Google Drive API
