import axios from 'axios';

// Configuration from .env
const CLIENT_ID = import.meta.env.VITE_CLIENT_ID;
const CLIENT_SECRET = import.meta.env.VITE_CLIENT_SECRET;
const REFRESH_TOKEN = import.meta.env.VITE_REFRESH_TOKEN;
const AUTH_USERNAME = import.meta.env.VITE_AUTH_USERNAME || 'admin';
const AUTH_PASSWORD = import.meta.env.VITE_AUTH_PASSWORD || 'admin';

let accessToken = null;
let tokenExpiresAt = null;

// Refresh Google Drive access token
const refreshAccessToken = async () => {
  try {
    console.log('Refreshing token with:', { CLIENT_ID, REFRESH_TOKEN: REFRESH_TOKEN ? 'present' : 'missing' });
    
    const response = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        refresh_token: REFRESH_TOKEN,
        grant_type: 'refresh_token'
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Token refresh error response:', errorData);
      throw new Error(`Token refresh failed: ${errorData.error_description || response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Token refreshed successfully');
    accessToken = data.access_token;
    tokenExpiresAt = Date.now() + (data.expires_in - 60) * 1000;
    localStorage.setItem('drive_access_token', accessToken);
    localStorage.setItem('drive_token_expires', tokenExpiresAt.toString());
    
    return accessToken;
  } catch (error) {
    console.error('Token refresh failed:', error);
    throw error;
  }
};

// Get valid access token
const getValidToken = async () => {
  const storedToken = localStorage.getItem('drive_access_token');
  const storedExpiry = localStorage.getItem('drive_token_expires');
  
  if (storedToken && storedExpiry && Date.now() < parseInt(storedExpiry)) {
    accessToken = storedToken;
    return accessToken;
  }
  
  return await refreshAccessToken();
};

// Authentication
export const authAPI = {
  login: async (username, password) => {
    if (username === AUTH_USERNAME && password === AUTH_PASSWORD) {
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('user', JSON.stringify({ username }));
      await refreshAccessToken(); // Get initial token
      return { success: true, user: { username } };
    }
    throw new Error('Invalid credentials');
  },
  
  logout: async () => {
    accessToken = null;
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
    localStorage.removeItem('drive_access_token');
    localStorage.removeItem('drive_token_expires');
    return { success: true };
  },
  
  checkAuth: async () => {
    const isAuth = localStorage.getItem('isAuthenticated');
    if (isAuth === 'true') {
      return { authenticated: true };
    }
    throw new Error('Not authenticated');
  },
  
  getToken: async () => {
    return await getValidToken();
  }
};

// Helper to extract file ID from Google Drive URL
const extractFileId = (url) => {
  const patterns = [
    /\/file\/d\/([a-zA-Z0-9-_]+)/,
    /id=([a-zA-Z0-9-_]+)/,
    /\/open\?id=([a-zA-Z0-9-_]+)/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  throw new Error('Invalid Google Drive URL');
};

// File operations - Direct Google Drive API
export const fileAPI = {
  // Get root items (both files and folders)
  getRootFolders: async () => {
    const token = await authAPI.getToken();
    if (!token) throw new Error('Not authenticated');
    
    const params = new URLSearchParams({
      pageSize: '1000',
      fields: 'files(id, name, mimeType, size, modifiedTime)',
      q: "'root' in parents and trashed=false",
      orderBy: 'folder,name asc'
    });
    
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files?${params}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (!response.ok) throw new Error('Failed to list folders');
    return response.json();
  },
  
  // Get subfolders in a folder
  getSubFolders: async (parentFolderId) => {
    const token = await authAPI.getToken();
    if (!token) throw new Error('Not authenticated');
    
    const params = new URLSearchParams({
      pageSize: '1000',
      fields: 'files(id, name, mimeType)',
      q: `'${parentFolderId}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'`,
      orderBy: 'name asc'
    });
    
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files?${params}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (!response.ok) throw new Error('Failed to list subfolders');
    return response.json();
  },
  
  // Get all items in a folder (both files and subfolders)
  getFilesInFolder: async (folderId) => {
    const token = await authAPI.getToken();
    if (!token) throw new Error('Not authenticated');
    
    const params = new URLSearchParams({
      pageSize: '1000',
      fields: 'files(id, name, size, mimeType, modifiedTime)',
      q: `'${folderId}' in parents and trashed=false`,
      orderBy: 'folder,name asc'
    });
    
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files?${params}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (!response.ok) throw new Error('Failed to list files');
    return response.json();
  },
  
  // List files in Google Drive (deprecated - use getRootFolders instead)
  listFiles: async (pageToken = null, pageSize = 100) => {
    const token = await authAPI.getToken();
    if (!token) throw new Error('Not authenticated');
    
    const params = new URLSearchParams({
      pageSize: pageSize.toString(),
      fields: 'nextPageToken, files(id, name, size, mimeType, modifiedTime, createdTime, webViewLink, iconLink)',
      orderBy: 'modifiedTime desc',
      q: "trashed=false and mimeType!='application/vnd.google-apps.folder'"
    });
    
    if (pageToken) params.append('pageToken', pageToken);
    
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files?${params}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (!response.ok) throw new Error('Failed to list files');
    return response.json();
  },
  
  // Get file metadata
  getFileMetadata: async (fileId) => {
    const token = await authAPI.getToken();
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files/${fileId}?fields=id,name,size,mimeType,modifiedTime,webViewLink,iconLink`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (!response.ok) throw new Error('Failed to get file metadata');
    return response.json();
  },
  
  // Transfer file from URL (copy from shared link)
  transferFile: async (driveUrl, fileName = null) => {
    const token = await authAPI.getToken();
    const fileId = extractFileId(driveUrl);
    
    // Copy file
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files/${fileId}/copy`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: fileName || 'Copied File'
        })
      }
    );
    
    if (!response.ok) throw new Error('Failed to copy file');
    const result = await response.json();
    
    return {
      success: true,
      fileName: result.name,
      fileId: result.id,
      fileSize: result.size || 'Unknown',
      mimeType: result.mimeType
    };
  },
  
  // Download file
  downloadFile: async (fileId) => {
    try {
      console.log('Starting download for file:', fileId);
      const token = await authAPI.getToken();
      console.log('Got token, length:', token?.length || 0);
      
      const metadata = await fileAPI.getFileMetadata(fileId);
      console.log('Got metadata:', metadata.name);
      
      // Check if it's a Google Workspace file (needs export)
      const googleMimeTypes = {
        'application/vnd.google-apps.document': { mimeType: 'application/pdf', extension: '.pdf' },
        'application/vnd.google-apps.spreadsheet': { mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', extension: '.xlsx' },
        'application/vnd.google-apps.presentation': { mimeType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation', extension: '.pptx' },
      };
      
      let downloadUrl;
      let fileName = metadata.name;
      
      if (googleMimeTypes[metadata.mimeType]) {
        // Export Google Workspace file
        const exportInfo = googleMimeTypes[metadata.mimeType];
        downloadUrl = `https://www.googleapis.com/drive/v3/files/${fileId}/export?mimeType=${encodeURIComponent(exportInfo.mimeType)}`;
        if (!fileName.endsWith(exportInfo.extension)) {
          fileName += exportInfo.extension;
        }
      } else {
        // Regular file download
        downloadUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;
      }
      
      console.log('Fetching from URL:', downloadUrl);
      const response = await fetch(downloadUrl, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Download error response:', errorText);
        throw new Error(`Failed to download file: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      console.log('Got blob, size:', blob.size);
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      a.style.display = 'none';
      document.body.appendChild(a);
      
      console.log('Triggering download for:', fileName);
      a.click();
      
      // Clean up
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        if (document.body.contains(a)) {
          document.body.removeChild(a);
        }
      }, 100);
      
      return { success: true, fileName };
    } catch (error) {
      console.error('Download function error:', error);
      throw error;
    }
  },
  
  // Upload from URL - Not possible in client-side only
  uploadFromUrl: async (downloadUrl, fileName = null) => {
    throw new Error('URL upload requires a backend server. Use browser extensions or download manually.');
  },
  
  // Get extraction progress - Simulated
  getProgress: async (taskId) => {
    return {
      status: 'completed',
      progress: 100
    };
  },
  
  // Delete file
  deleteFile: async (fileId) => {
    const token = await authAPI.getToken();
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files/${fileId}`,
      {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (!response.ok) throw new Error('Failed to delete file');
    return { success: true, message: 'File deleted' };
  },
  
  // Create folder in Drive
  createFolder: async (folderName, parentId = 'root') => {
    const token = await authAPI.getToken();
    const response = await fetch(
      'https://www.googleapis.com/drive/v3/files',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: folderName,
          mimeType: 'application/vnd.google-apps.folder',
          parents: [parentId]
        })
      }
    );
    
    if (!response.ok) throw new Error('Failed to create folder');
    return response.json();
  },
  
  // Upload file to Drive
  uploadFile: async (file, fileName, parentId = 'root', onProgress) => {
    const token = await authAPI.getToken();
    
    const metadata = {
      name: fileName,
      parents: [parentId]
    };
    
    const formData = new FormData();
    formData.append('metadata', new Blob([JSON.stringify(metadata)], { type: 'application/json' }));
    formData.append('file', file);
    
    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const percentComplete = (e.loaded / e.total) * 100;
          onProgress(percentComplete);
        }
      });
      
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error('Upload failed'));
        }
      });
      
      xhr.addEventListener('error', () => reject(new Error('Upload failed')));
      
      xhr.open('POST', 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart');
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);
    });
  },
  
  // Extract archive (zip/rar) to Drive
  extractArchive: async (fileId, onProgress) => {
    const token = await authAPI.getToken();
    
    // Get file metadata
    const metadata = await fileAPI.getFileMetadata(fileId);
    const fileName = metadata.name;
    const fileExtension = fileName.split('.').pop().toLowerCase();
    
    if (!['zip', 'rar'].includes(fileExtension)) {
      throw new Error('Only .zip and .rar files can be extracted');
    }
    
    if (fileExtension === 'rar') {
      throw new Error('.rar extraction is not supported yet. Please use .zip files.');
    }
    
    onProgress?.({ status: 'downloading', progress: 10, message: 'Downloading archive...' });
    
    // Download the archive
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (!response.ok) throw new Error('Failed to download archive');
    
    const blob = await response.blob();
    
    onProgress?.({ status: 'extracting', progress: 30, message: 'Extracting files...' });
    
    // Extract using JSZip
    const JSZip = (await import('jszip')).default;
    const zip = await JSZip.loadAsync(blob);
    
    // Create extraction folder
    const folderName = fileName.replace(/\.[^/.]+$/, '') + '_extracted';
    onProgress?.({ status: 'creating', progress: 40, message: 'Creating folder...' });
    
    const folder = await fileAPI.createFolder(folderName);
    
    // Get all files
    const files = Object.keys(zip.files).filter(name => !zip.files[name].dir);
    const totalFiles = files.length;
    let uploadedFiles = 0;
    
    onProgress?.({ 
      status: 'uploading', 
      progress: 50, 
      message: `Uploading ${totalFiles} files...`,
      totalFiles,
      uploadedFiles: 0
    });
    
    // Upload each file
    for (const fileName of files) {
      const fileData = await zip.files[fileName].async('blob');
      
      await fileAPI.uploadFile(
        fileData,
        fileName,
        folder.id,
        (percent) => {
          const baseProgress = 50 + (uploadedFiles / totalFiles) * 45;
          const fileProgress = (percent / 100) * (45 / totalFiles);
          onProgress?.({
            status: 'uploading',
            progress: Math.round(baseProgress + fileProgress),
            message: `Uploading ${fileName}...`,
            totalFiles,
            uploadedFiles,
            currentFile: fileName
          });
        }
      );
      
      uploadedFiles++;
      onProgress?.({
        status: 'uploading',
        progress: 50 + Math.round((uploadedFiles / totalFiles) * 45),
        message: `Uploaded ${uploadedFiles}/${totalFiles} files`,
        totalFiles,
        uploadedFiles
      });
    }
    
    onProgress?.({ 
      status: 'completed', 
      progress: 100, 
      message: `Extracted ${totalFiles} files to "${folderName}"`,
      totalFiles,
      uploadedFiles: totalFiles
    });
    
    return { 
      success: true, 
      folderName,
      folderId: folder.id,
      filesExtracted: totalFiles
    };
  },
};

// Search
export const searchAPI = {
  searchFiles: async (query) => {
    const token = await authAPI.getToken();
    const params = new URLSearchParams({
      q: `name contains '${query}' and trashed=false`,
      fields: 'files(id, name, size, mimeType, modifiedTime)',
      pageSize: '50'
    });
    
    const response = await fetch(
      `https://www.googleapis.com/drive/v3/files?${params}`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (!response.ok) throw new Error('Search failed');
    return response.json();
  },
};
