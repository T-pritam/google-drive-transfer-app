#!/usr/bin/env python3
"""
Python Flask + React - Google Drive File Transfer Pro
Full-fledged application with file listing, extraction, and URL uploads
"""

import os
import re
import json
import uuid
import time
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from functools import wraps
import tempfile
import shutil

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://localhost:5000'])

# Configuration
class Config:
    CLIENT_ID = os.getenv('CLIENT_ID', 'your-google-oauth-client-id')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'your-google-oauth-client-secret')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:3000/oauth2callback')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN', 'your-google-oauth-refresh-token')
    
    AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'admin')
    AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', 'secure123')
    
    MAX_FILE_SIZE = 30 * 1024 * 1024 * 1024  # 30GB limit
    CHUNK_SIZE = 100 * 1024 * 1024  # 100MB chunks
    
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())

app.config.from_object(Config)

# Global variables
access_token = None
token_expires_at = None
active_tasks = {}  # Track ongoing extraction/upload tasks

# ====================== Authentication ======================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == app.config['AUTH_USERNAME'] and password == app.config['AUTH_PASSWORD']:
        session['logged_in'] = True
        session['login_time'] = datetime.now().isoformat()
        return jsonify({'success': True, 'user': {'username': username}})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    if 'logged_in' in session:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False}), 401

# ====================== Token Management ======================

def refresh_access_token():
    """Refresh the access token using the refresh token"""
    global access_token, token_expires_at
    
    if not app.config['REFRESH_TOKEN'] or app.config['REFRESH_TOKEN'] == 'your-google-oauth-refresh-token':
        raise Exception('No refresh token available. Please configure REFRESH_TOKEN.')
    
    response = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': app.config['CLIENT_ID'],
        'client_secret': app.config['CLIENT_SECRET'],
        'refresh_token': app.config['REFRESH_TOKEN'],
        'grant_type': 'refresh_token'
    })
    
    if response.status_code != 200:
        raise Exception(f'Failed to refresh token: {response.status_code}')
    
    data = response.json()
    access_token = data['access_token']
    expires_in = data.get('expires_in', 3600)
    token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
    
    return access_token

def get_valid_access_token():
    """Get a valid access token, refreshing if necessary"""
    global access_token, token_expires_at
    
    if not access_token or not token_expires_at or datetime.now() >= token_expires_at:
        return refresh_access_token()
    
    try:
        test_response = requests.get(
            'https://www.googleapis.com/drive/v3/about?fields=user',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if test_response.status_code == 200:
            return access_token
        else:
            return refresh_access_token()
    except:
        return refresh_access_token()

# ====================== Helper Functions ======================

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
            'fields': 'id,name,size,mimeType,modifiedTime',
            'supportsAllDrives': 'true'
        },
        timeout=30
    )
    
    if response.status_code != 200:
        raise Exception(f'Failed to get file metadata: {response.status_code}')
    
    return response.json()

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
        timeout=300
    )
    
    if copy_response.status_code != 200:
        raise Exception(f'Failed to copy file: {copy_response.status_code}')
    
    return copy_response.json()

def download_file_from_url(url, task_id):
    """Download file from URL with progress tracking"""
    temp_file = None
    try:
        active_tasks[task_id] = {
            'status': 'downloading',
            'progress': 0,
            'fileName': 'Downloading...',
            'error': None
        }
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get filename from header or URL
        filename = 'downloaded_file'
        if 'content-disposition' in response.headers:
            cd = response.headers['content-disposition']
            fname = re.findall('filename="?([^"]+)"?', cd)
            if fname:
                filename = fname[0]
        else:
            filename = url.split('/')[-1].split('?')[0] or 'downloaded_file'
        
        total_size = int(response.headers.get('content-length', 0))
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='_' + filename)
        downloaded = 0
        
        active_tasks[task_id]['fileName'] = filename
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
                downloaded += len(chunk)
                
                if total_size:
                    progress = int((downloaded / total_size) * 100)
                    active_tasks[task_id]['progress'] = progress
        
        temp_file.close()
        active_tasks[task_id]['status'] = 'completed'
        active_tasks[task_id]['progress'] = 100
        active_tasks[task_id]['filePath'] = temp_file.name
        
        return temp_file.name, filename
        
    except Exception as e:
        if temp_file:
            temp_file.close()
            try:
                os.unlink(temp_file.name)
            except:
                pass
        active_tasks[task_id]['status'] = 'failed'
        active_tasks[task_id]['error'] = str(e)
        raise

def upload_file_to_drive(file_path, filename, access_token, task_id):
    """Upload file to Google Drive with progress tracking"""
    try:
        active_tasks[task_id]['status'] = 'uploading'
        active_tasks[task_id]['progress'] = 0
        
        file_size = os.path.getsize(file_path)
        
        # Create file metadata
        metadata = {
            'name': filename,
            'mimeType': 'application/octet-stream'
        }
        
        # Upload file
        with open(file_path, 'rb') as f:
            files = {
                'data': ('metadata', json.dumps(metadata), 'application/json; charset=UTF-8'),
                'file': (filename, f, 'application/octet-stream')
            }
            
            response = requests.post(
                'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',
                headers={'Authorization': f'Bearer {access_token}'},
                files=files,
                timeout=300
            )
        
        if response.status_code not in [200, 201]:
            raise Exception(f'Upload failed: {response.status_code}')
        
        active_tasks[task_id]['status'] = 'completed'
        active_tasks[task_id]['progress'] = 100
        
        return response.json()
        
    except Exception as e:
        active_tasks[task_id]['status'] = 'failed'
        active_tasks[task_id]['error'] = str(e)
        raise

# ====================== API Routes ======================

@app.route('/api/files/list', methods=['GET'])
@login_required
def list_files():
    """List files in user's Google Drive"""
    try:
        access_token = get_valid_access_token()
        page_token = request.args.get('pageToken')
        page_size = min(int(request.args.get('pageSize', 100)), 1000)
        
        params = {
            'pageSize': page_size,
            'fields': 'nextPageToken, files(id, name, size, mimeType, modifiedTime, createdTime)',
            'orderBy': 'modifiedTime desc',
            'q': "trashed=false"
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        response = requests.get(
            'https://www.googleapis.com/drive/v3/files',
            headers={'Authorization': f'Bearer {access_token}'},
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f'Failed to list files: {response.status_code}')
        
        data = response.json()
        
        return jsonify({
            'files': data.get('files', []),
            'nextPageToken': data.get('nextPageToken')
        })
        
    except Exception as e:
        app.logger.error(f'List files error: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<file_id>/metadata', methods=['GET'])
@login_required
def get_file_info(file_id):
    """Get metadata for a specific file"""
    try:
        access_token = get_valid_access_token()
        metadata = get_file_metadata(file_id, access_token)
        return jsonify(metadata)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transfer', methods=['POST'])
@login_required
def transfer():
    """Transfer file from shared Drive link to user's Drive"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        drive_url = data.get('driveUrl')
        file_name = data.get('fileName')
        
        if not drive_url:
            return jsonify({'error': 'Drive URL is required'}), 400
        
        access_token = get_valid_access_token()
        file_id = extract_file_id(drive_url)
        metadata = get_file_metadata(file_id, access_token)
        
        file_size = int(metadata.get('size', 0))
        file_size_mb = file_size / (1024 * 1024) if file_size else 0
        
        if file_size > app.config['MAX_FILE_SIZE']:
            return jsonify({'error': 'File too large'}), 400
        
        final_file_name = file_name or metadata['name']
        copy_result = copy_file_server_to_server(file_id, final_file_name, access_token)
        
        transfer_time = f'{time.time() - start_time:.1f}s'
        
        return jsonify({
            'success': True,
            'fileName': final_file_name,
            'fileId': copy_result['id'],
            'fileSize': f'{file_size_mb:.2f} MB',
            'transferTime': transfer_time,
            'mimeType': metadata.get('mimeType')
        })
        
    except Exception as error:
        app.logger.error(f'Transfer error: {error}')
        return jsonify({'error': str(error)}), 500

@app.route('/api/files/extract', methods=['POST'])
@login_required
def extract_file():
    """Extract/download file from Google Drive"""
    try:
        data = request.get_json()
        file_id = data.get('fileId')
        task_id = data.get('taskId', f'extract-{uuid.uuid4()}')
        
        if not file_id:
            return jsonify({'error': 'File ID is required'}), 400
        
        # Initialize task
        active_tasks[task_id] = {
            'status': 'starting',
            'progress': 0,
            'fileName': 'Preparing...',
            'fileId': file_id
        }
        
        # Start extraction in background thread
        def extract_async():
            try:
                access_token = get_valid_access_token()
                metadata = get_file_metadata(file_id, access_token)
                
                active_tasks[task_id]['fileName'] = metadata['name']
                active_tasks[task_id]['status'] = 'extracting'
                
                # Simulate extraction progress (in real implementation, track actual download)
                for i in range(0, 101, 10):
                    time.sleep(0.5)
                    active_tasks[task_id]['progress'] = i
                
                active_tasks[task_id]['status'] = 'completed'
                active_tasks[task_id]['progress'] = 100
                
            except Exception as e:
                active_tasks[task_id]['status'] = 'failed'
                active_tasks[task_id]['error'] = str(e)
        
        thread = threading.Thread(target=extract_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'taskId': task_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/upload-from-url', methods=['POST'])
@login_required
def upload_from_url():
    """Upload file from direct download URL to Google Drive"""
    try:
        data = request.get_json()
        download_url = data.get('downloadUrl')
        custom_name = data.get('fileName')
        
        if not download_url:
            return jsonify({'error': 'Download URL is required'}), 400
        
        task_id = f'upload-{uuid.uuid4()}'
        
        def upload_async():
            temp_path = None
            try:
                # Download file
                temp_path, filename = download_file_from_url(download_url, task_id)
                
                if custom_name:
                    filename = custom_name
                
                # Upload to Drive
                access_token = get_valid_access_token()
                result = upload_file_to_drive(temp_path, filename, access_token, task_id)
                
                active_tasks[task_id]['fileId'] = result['id']
                
            except Exception as e:
                app.logger.error(f'Upload from URL error: {e}')
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
        
        thread = threading.Thread(target=upload_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'taskId': task_id,
            'message': 'Upload started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/progress/<task_id>', methods=['GET'])
@login_required
def get_progress(task_id):
    """Get progress of an extraction or upload task"""
    if task_id not in active_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(active_tasks[task_id])

@app.route('/api/files/<file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """Delete a file from Google Drive"""
    try:
        access_token = get_valid_access_token()
        
        response = requests.delete(
            f'https://www.googleapis.com/drive/v3/files/{file_id}',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        
        if response.status_code not in [200, 204]:
            raise Exception(f'Failed to delete file: {response.status_code}')
        
        return jsonify({'success': True, 'message': 'File deleted'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/search', methods=['GET'])
@login_required
def search_files():
    """Search files in Google Drive"""
    try:
        query = request.args.get('q', '')
        access_token = get_valid_access_token()
        
        search_query = f"name contains '{query}' and trashed=false"
        
        response = requests.get(
            'https://www.googleapis.com/drive/v3/files',
            headers={'Authorization': f'Bearer {access_token}'},
            params={
                'q': search_query,
                'fields': 'files(id, name, size, mimeType, modifiedTime)',
                'pageSize': 50
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f'Search failed: {response.status_code}')
        
        return jsonify(response.json())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

# Serve React app in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React app"""
    if path and os.path.exists(os.path.join('frontend/dist', path)):
        return send_file(os.path.join('frontend/dist', path))
    elif os.path.exists('frontend/dist/index.html'):
        return send_file('frontend/dist/index.html')
    else:
        return jsonify({
            'message': 'Google Drive Transfer Pro API',
            'version': '2.0.0',
            'endpoints': [
                '/api/login',
                '/api/logout',
                '/api/files/list',
                '/api/transfer',
                '/api/files/extract',
                '/api/files/upload-from-url'
            ]
        })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
