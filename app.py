#!/usr/bin/env python3
"""
Python Flask - Google Drive File Transfer
Direct transfer from shared Google Drive links to personal Google Drive
Same functionality as the Cloudflare Worker but in Python
"""

import os
import re
import json
import uuid
import time
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, make_response
from functools import wraps

app = Flask(__name__)

# Configuration - Use environment variables for production
class Config:
    # Your actual Google OAuth credentials
    CLIENT_ID = os.getenv('CLIENT_ID', 'your-google-oauth-client-id')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'your-google-oauth-client-secret')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:3000/oauth2callback')
    
    # Get refresh token from environment or use default
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN', 'your-google-oauth-refresh-token')
    
    # Simple authentication (change these credentials)
    AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'admin')
    AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', 'secure123')
    
    # File size limits to prevent memory issues
    MAX_FILE_SIZE = 30 * 1024 * 1024 * 1024  # 10GB limit
    CHUNK_SIZE = 100 * 1024 * 1024  # 100MB chunks
    
    # Flask secret key for sessions
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())

app.config.from_object(Config)

# Global variables for token management
access_token = None
token_expires_at = None

# HTML Templates (same as Cloudflare Worker)
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Drive Transfer - Login</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-header h1 {
            color: #333;
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }
        
        .login-header p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .login-btn {
            width: 100%;
            padding: 0.75rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
        }
        
        .error {
            color: #e74c3c;
            font-size: 0.9rem;
            margin-top: 1rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🚀 Drive Transfer</h1>
            <p>Secure file transfer to your Google Drive</p>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="login-btn">Login</button>
            
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

HOMEPAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Drive Transfer</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            position: relative;
        }
        
        .header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .logout {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
            text-decoration: none;
        }
        
        .logout:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .content {
            padding: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 600;
        }
        
        input[type="url"],
        input[type="text"] {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input[type="url"]:focus,
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .transfer-btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            margin-bottom: 2rem;
        }
        
        .transfer-btn:hover {
            transform: translateY(-2px);
        }
        
        .transfer-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            background: #f8f9fa;
            border-radius: 5px;
            padding: 1.5rem;
            min-height: 200px;
            border: 2px solid #e9ecef;
        }
        
        .status h3 {
            color: #333;
            margin-bottom: 1rem;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .status-item:last-child {
            border-bottom: none;
        }
        
        .status-label {
            font-weight: 500;
            color: #666;
        }
        
        .status-value {
            font-weight: 600;
            color: #333;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            margin-top: 1rem;
            border: 1px solid #f5c6cb;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            margin-top: 1rem;
            border: 1px solid #c3e6cb;
        }
        
        .example {
            font-size: 0.85rem;
            color: #666;
            margin-top: 0.25rem;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/logout" class="logout">Logout</a>
            <h1>🚀 Google Drive Transfer</h1>
            <p>Transfer files from shared Google Drive links to your personal Drive</p>
        </div>
        
        <div class="content">
            <form id="transferForm">
                <div class="form-group">
                    <label for="driveUrl">Google Drive Share URL</label>
                    <input type="url" id="driveUrl" name="driveUrl" required 
                           placeholder="https://drive.google.com/file/d/1ABC...">
                    <div class="example">Example: https://drive.google.com/file/d/1ABC123.../view?usp=sharing</div>
                </div>
                
                <div class="form-group">
                    <label for="fileName">Save as filename (optional)</label>
                    <input type="text" id="fileName" name="fileName" 
                           placeholder="Leave empty to keep original name">
                    <div class="example">Example: my-document.pdf</div>
                </div>
                
                <button type="submit" class="transfer-btn" id="transferBtn">
                    🚀 Start Transfer
                </button>
            </form>
            
            <div class="status" id="statusPanel">
                <h3>📊 Transfer Status</h3>
                <div id="statusContent">
                    <p style="color: #666; text-align: center; margin-top: 2rem;">
                        Ready to transfer files. Fill in the form above and click "Start Transfer".
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('transferForm');
        const transferBtn = document.getElementById('transferBtn');
        const statusPanel = document.getElementById('statusPanel');
        const statusContent = document.getElementById('statusContent');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const driveUrl = document.getElementById('driveUrl').value;
            const fileName = document.getElementById('fileName').value;
            
            if (!driveUrl) {
                showError('Please enter a Google Drive URL');
                return;
            }
            
            await startTransfer(driveUrl, fileName);
        });

        async function startTransfer(driveUrl, fileName) {
            transferBtn.disabled = true;
            transferBtn.textContent = '🔄 Transferring...';
            
            showStatus('⏳ Checking file size and permissions...', 'info');
            
            try {
                const response = await fetch('/transfer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        driveUrl: driveUrl,
                        fileName: fileName
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showTransferSuccess(result);
                } else {
                    showError(result.error || 'Transfer failed', result.details);
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                transferBtn.disabled = false;
                transferBtn.textContent = '🚀 Start Transfer';
            }
        }

        function showStatus(message, type = 'info') {
            const statusHtml = `
                <div class="status-item">
                    <span class="status-label">Status:</span>
                    <span class="status-value">${message}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 20%"></div>
                </div>
            `;
            statusContent.innerHTML = statusHtml;
        }

        function showTransferSuccess(result) {
            const statusHtml = `
                <div class="success">
                    ✅ Transfer completed successfully!
                </div>
                <div class="status-item">
                    <span class="status-label">File Name:</span>
                    <span class="status-value">${result.fileName}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">File Size:</span>
                    <span class="status-value">${result.fileSize || 'Unknown'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Transfer Time:</span>
                    <span class="status-value">${result.transferTime || 'Unknown'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Google Drive File ID:</span>
                    <span class="status-value">${result.fileId}</span>
                </div>
                ${result.mimeType ? `
                <div class="status-item">
                    <span class="status-label">File Type:</span>
                    <span class="status-value">${result.mimeType}</span>
                </div>
                ` : ''}
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 100%"></div>
                </div>
            `;
            statusContent.innerHTML = statusHtml;
        }

        function showError(message, details = '') {
            const statusHtml = `
                <div class="error">
                    ❌ Error: ${message}
                </div>
                ${details ? `
                <div class="status-item">
                    <span class="status-label">Details:</span>
                    <span class="status-value" style="font-size: 0.85rem; word-break: break-word;">${details}</span>
                </div>
                ` : ''}
                <div class="status-item">
                    <span class="status-label">Status:</span>
                    <span class="status-value">Failed</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Troubleshooting:</span>
                    <span class="status-value" style="font-size: 0.85rem;">
                        • Check if file is publicly accessible<br>
                        • Try with a smaller file (max 10GB)<br>
                        • Verify the Google Drive URL format
                    </span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%; background: #dc3545;"></div>
                </div>
            `;
            statusContent.innerHTML = statusHtml;
        }
    </script>
</body>
</html>
"""

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Token management functions
def refresh_access_token():
    """Refresh the access token using the refresh token"""
    global access_token, token_expires_at
    
    if not app.config['REFRESH_TOKEN']:
        raise Exception('No refresh token available. Please run the OAuth flow first.')
    
    response = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': app.config['CLIENT_ID'],
        'client_secret': app.config['CLIENT_SECRET'],
        'refresh_token': app.config['REFRESH_TOKEN'],
        'grant_type': 'refresh_token'
    })
    
    if response.status_code != 200:
        raise Exception(f'Failed to refresh token: {response.status_code} - {response.text}')
    
    data = response.json()
    access_token = data['access_token']
    expires_in = data.get('expires_in', 3600)
    token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 minute early
    
    return access_token

def get_valid_access_token():
    """Get a valid access token, refreshing if necessary"""
    global access_token, token_expires_at
    
    if not access_token or not token_expires_at or datetime.now() >= token_expires_at:
        return refresh_access_token()
    
    # Test if current token still works
    try:
        test_response = requests.get(
            'https://www.googleapis.com/drive/v3/about?fields=user',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if test_response.status_code == 200:
            return access_token
        else:
            # Token expired, refresh it
            return refresh_access_token()
    except:
        # Token invalid, refresh it
        return refresh_access_token()

# Helper functions
def extract_file_id(url):
    """Extract file ID from Google Drive URL"""
    patterns = [
        r'/file/d/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)',
        r'/open\?id=([a-zA-Z0-9-_]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError('Invalid Google Drive URL format')

def get_file_metadata(file_id, access_token):
    """Get file metadata from Google Drive"""
    response = requests.get(
        f'https://www.googleapis.com/drive/v3/files/{file_id}',
        headers={'Authorization': f'Bearer {access_token}'},
        params={
            'fields': 'id,name,size,mimeType',
            'supportsAllDrives': 'true'
        },
        timeout=30
    )
    
    if response.status_code != 200:
        raise Exception(f'Failed to get file metadata: {response.status_code} - {response.text}')
    
    metadata = response.json()
    
    # Check file size limit
    if metadata.get('size'):
        file_size = int(metadata['size'])
        if file_size > app.config['MAX_FILE_SIZE']:
            size_gb = file_size / (1024**3)
            limit_gb = app.config['MAX_FILE_SIZE'] / (1024**3)
            raise Exception(f'File too large: {size_gb:.2f}GB. Maximum allowed: {limit_gb:.0f}GB')
    
    return metadata

def copy_file_server_to_server(source_file_id, new_name, access_token):
    """Copy file using Google Drive's server-to-server copy API"""
    copy_response = requests.post(
        f'https://www.googleapis.com/drive/v3/files/{source_file_id}/copy',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        params={'supportsAllDrives': 'true'},
        json={'name': new_name},
        timeout=300  # 5 minutes timeout for large files
    )
    
    if copy_response.status_code != 200:
        raise Exception(f'Failed to copy file: {copy_response.status_code} - {copy_response.text}')
    
    return copy_response.json()

# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == app.config['AUTH_USERNAME'] and password == app.config['AUTH_PASSWORD']:
            session['logged_in'] = True
            session['login_time'] = datetime.now().isoformat()
            return render_template_string(HOMEPAGE)
        else:
            return render_template_string(LOGIN_PAGE, error='Invalid credentials'), 401
    
    if 'logged_in' in session:
        return render_template_string(HOMEPAGE)
    else:
        return render_template_string(LOGIN_PAGE)

@app.route('/transfer', methods=['POST'])
@login_required
def transfer():
    start_time = time.time()
    
    try:
        data = request.get_json()
        drive_url = data.get('driveUrl')
        file_name = data.get('fileName')
        
        if not drive_url:
            return jsonify({'error': 'Drive URL is required'}), 400
        
        # Get valid access token (refresh if needed)
        access_token = get_valid_access_token()
        
        # Extract file ID from URL
        file_id = extract_file_id(drive_url)
        
        # Get file metadata with size checking
        metadata = get_file_metadata(file_id, access_token)
        
        # Calculate file size
        file_size = int(metadata.get('size', 0))
        file_size_mb = file_size / (1024 * 1024) if file_size else 0
        
        # Use provided filename or original name
        final_file_name = file_name or metadata['name']
        
        # Perform server-to-server copy (no download/upload needed!)
        copy_result = copy_file_server_to_server(file_id, final_file_name, access_token)
        
        transfer_time = f'{time.time() - start_time:.1f}s'
        
        return jsonify({
            'success': True,
            'fileName': final_file_name,
            'fileId': copy_result['id'],
            'fileSize': f'{file_size_mb:.2f} MB',
            'transferTime': transfer_time,
            'originalFileId': file_id,
            'mimeType': metadata.get('mimeType')
        })
        
    except Exception as error:
        app.logger.error(f'Transfer error: {error}')
        
        # Provide specific error messages
        error_message = str(error)
        error_details = str(error)
        
        # Handle specific error types
        if 'File too large' in error_message:
            error_message = 'File too large for transfer. Try a smaller file (max 10GB).'
        elif 'Failed to get file metadata' in error_message:
            error_message = 'Cannot access the file. Make sure the Google Drive link is public or shared with your account.'
        elif 'Invalid Google Drive URL' in error_message:
            error_message = 'Invalid Google Drive URL format. Please use a proper share link.'
        elif 'No refresh token' in error_message:
            error_message = 'Authentication error. Please update your refresh token in the configuration.'
        
        return jsonify({
            'error': error_message,
            'details': error_details,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/health')
def health():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # For development
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
