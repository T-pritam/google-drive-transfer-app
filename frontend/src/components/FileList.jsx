import { useEffect, useState } from 'react';
import { ChevronRight, ChevronDown, Folder, File, Image, Video, Music, FileText, Archive, Download, Trash2, Check } from 'lucide-react';
import { fileAPI } from '../api/client';

const getFileIcon = (mimeType) => {
  if (!mimeType) return File;
  if (mimeType.includes('image')) return Image;
  if (mimeType.includes('video')) return Video;
  if (mimeType.includes('audio')) return Music;
  if (mimeType.includes('text') || mimeType.includes('document')) return FileText;
  if (mimeType.includes('zip') || mimeType.includes('compressed')) return Archive;
  return File;
};

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A';
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const isFolder = (mimeType) => {
  return mimeType === 'application/vnd.google-apps.folder';
};

const isArchive = (fileName, mimeType) => {
  const extension = fileName?.split('.').pop()?.toLowerCase();
  return extension === 'zip' || extension === 'rar' || 
         mimeType?.includes('zip') || mimeType?.includes('rar') || 
         mimeType?.includes('compressed');
};

export default function FileList() {
  const [items, setItems] = useState([]);
  const [expandedFolders, setExpandedFolders] = useState({});
  const [folderContents, setFolderContents] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [extracting, setExtracting] = useState({});
  const [extractProgress, setExtractProgress] = useState({});

  // Load root items on mount
  useEffect(() => {
    loadRootItems();
  }, []);

  const loadRootItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fileAPI.getRootFolders();
      setItems(data.files || []);
    } catch (err) {
      setError(err.message || 'Failed to load items');
    } finally {
      setLoading(false);
    }
  };

  const toggleFolder = async (folderId) => {
    if (expandedFolders[folderId]) {
      // Collapse
      setExpandedFolders(prev => {
        const newState = { ...prev };
        delete newState[folderId];
        return newState;
      });
    } else {
      // Expand and load contents
      try {
        const data = await fileAPI.getFilesInFolder(folderId);
        setFolderContents(prev => ({
          ...prev,
          [folderId]: data.files || []
        }));
        setExpandedFolders(prev => ({
          ...prev,
          [folderId]: true
        }));
      } catch (err) {
        alert('Failed to load folder contents: ' + err.message);
      }
    }
  };

  const handleDownload = async (fileId, fileName) => {
    console.log('handleDownload called for:', fileName);
    setExtracting(prev => ({ ...prev, [fileId]: { progress: 50, status: 'downloading', message: 'Downloading...' } }));

    try {
      console.log('Calling fileAPI.downloadFile');
      await fileAPI.downloadFile(fileId);
      console.log('Download completed');
      
      setExtracting(prev => ({
        ...prev,
        [fileId]: { progress: 100, status: 'completed', message: 'Downloaded' }
      }));

      setTimeout(() => {
        setExtracting(prev => {
          const newState = { ...prev };
          delete newState[fileId];
          return newState;
        });
      }, 2000);

    } catch (err) {
      console.error('Download handler error:', err);
      setExtracting(prev => {
        const newState = { ...prev };
        delete newState[fileId];
        return newState;
      });
      alert('Failed to download file: ' + err.message);
    }
  };

  const handleExtractArchive = async (fileId, fileName) => {
    setExtractProgress(prev => ({ ...prev, [fileId]: { progress: 0, status: 'starting', message: 'Starting extraction...', totalFiles: 0, uploadedFiles: 0 } }));

    try {
      await fileAPI.extractArchive(fileId, (progressInfo) => {
        setExtractProgress(prev => ({
          ...prev,
          [fileId]: progressInfo
        }));
      });
      
      // Keep the completed status for 3 seconds
      setTimeout(() => {
        setExtractProgress(prev => {
          const newState = { ...prev };
          delete newState[fileId];
          return newState;
        });
        // Reload the current view
        loadRootItems();
      }, 3000);

    } catch (err) {
      console.error('Extraction error:', err);
      setExtractProgress(prev => {
        const newState = { ...prev };
        delete newState[fileId];
        return newState;
      });
      alert('Failed to extract archive: ' + err.message);
    }
  };

  const handleDelete = async (fileId) => {
    if (!confirm('Are you sure you want to delete this file?')) return;
    
    try {
      await fileAPI.deleteFile(fileId);
      // Reload root items and expanded folders
      loadRootItems();
      Object.keys(expandedFolders).forEach(folderId => {
        if (expandedFolders[folderId]) {
          fileAPI.getFilesInFolder(folderId).then(data => {
            setFolderContents(prev => ({
              ...prev,
              [folderId]: data.files || []
            }));
          });
        }
      });
    } catch (err) {
      alert('Failed to delete file: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-600 border-t-transparent"></div>
        <p className="mt-4 text-gray-600">Loading folders...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
        <div className="text-red-500 mb-2">⚠️ Error loading items</div>
        <p className="text-gray-600">{error}</p>
        <button
          onClick={loadRootItems}
          className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
        <div className="text-gray-400 mb-2">📁 No items found</div>
        <p className="text-gray-600">Your Google Drive appears to be empty</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">My Google Drive</h2>
        <p className="text-sm text-gray-500 mt-1">{items.length} items</p>
      </div>

      <div className="divide-y divide-gray-200">
        {items.map(item => (
          <ItemRow
            key={item.id}
            item={item}
            depth={0}
            expandedFolders={expandedFolders}
            folderContents={folderContents}
            toggleFolder={toggleFolder}
            handleDownload={handleDownload}
            handleExtractArchive={handleExtractArchive}
            handleDelete={handleDelete}
            extracting={extracting}
            extractProgress={extractProgress}
          />
        ))}
      </div>
    </div>
  );
}

// ItemRow component to render files and folders recursively
function ItemRow({ item, depth, expandedFolders, folderContents, toggleFolder, handleDownload, handleExtractArchive, handleDelete, extracting, extractProgress }) {
  const isItemFolder = isFolder(item.mimeType);
  const isItemArchive = !isItemFolder && isArchive(item.name, item.mimeType);
  const isExpanded = expandedFolders[item.id];
  const contents = folderContents[item.id] || [];
  const isExtracting = extracting[item.id];
  const extractState = extractProgress[item.id];
  const IconComponent = isItemFolder ? Folder : getFileIcon(item.mimeType);
  const paddingLeft = `${depth * 1.5 + 1}rem`;

  return (
    <>
      <div className="hover:bg-gray-50 transition">
        <div className="p-4 flex items-center justify-between" style={{ paddingLeft }}>
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            {isItemFolder && (
              <button
                onClick={() => toggleFolder(item.id)}
                className="p-1 hover:bg-gray-200 rounded transition flex-shrink-0"
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4 text-gray-600" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-600" />
                )}
              </button>
            )}
            {!isItemFolder && <div className="w-6"></div>}
            <IconComponent className={`w-5 h-5 flex-shrink-0 ${isItemFolder ? 'text-blue-500' : 'text-gray-400'}`} />
            <div className="min-w-0 flex-1">
              <div
                className={`text-sm truncate ${
                  isItemFolder ? 'font-medium text-gray-900 cursor-pointer' : 'text-gray-900'
                }`}
                onClick={() => isItemFolder && toggleFolder(item.id)}
              >
                {item.name}
              </div>
              {!isItemFolder && (
                <div className="text-xs text-gray-500">
                  {formatFileSize(item.size)} • {formatDate(item.modifiedTime)}
                </div>
              )}
            </div>
          </div>

          {!isItemFolder && (
            <div className="flex items-center space-x-2 ml-4">
              {extractState ? (
                <div className="flex flex-col items-end min-w-[200px]">
                  <div className="text-xs font-medium text-gray-700 mb-1">{extractState.message}</div>
                  <div className="flex items-center space-x-2 w-full">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          extractState.status === 'completed' ? 'bg-green-500' :
                          extractState.status === 'failed' ? 'bg-red-500' :
                          'bg-purple-600'
                        }`}
                        style={{ width: `${extractState.progress || 0}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600 min-w-[3rem] text-right">
                      {extractState.progress}%
                    </span>
                  </div>
                  {extractState.totalFiles > 0 && (
                    <div className="text-xs text-gray-500 mt-1">
                      {extractState.uploadedFiles}/{extractState.totalFiles} files
                    </div>
                  )}
                </div>
              ) : isExtracting ? (
                isExtracting.status === 'completed' ? (
                  <div className="text-xs text-green-600 font-medium">✓ Downloaded</div>
                ) : (
                  <div className="text-xs text-gray-600">{isExtracting.progress}%</div>
                )
              ) : (
                <>
                  {isItemArchive && (
                    <button
                      onClick={() => handleExtractArchive(item.id, item.name)}
                      className="px-3 py-1.5 bg-green-600 text-white rounded hover:bg-green-700 transition text-xs font-medium flex items-center space-x-1"
                      title="Extract archive to Drive"
                    >
                      <Archive className="w-3.5 h-3.5" />
                      <span>Extract</span>
                    </button>
                  )}
                  <button
                    onClick={() => handleDownload(item.id, item.name)}
                    className="p-1.5 bg-purple-600 text-white rounded hover:bg-purple-700 transition"
                    title="Download"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="p-1.5 bg-red-600 text-white rounded hover:bg-red-700 transition"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Render folder contents */}
      {isItemFolder && isExpanded && (
        <div className="bg-gray-50">
          {contents.length > 0 ? (
            contents.map(subItem => (
              <ItemRow
                key={subItem.id}
                item={subItem}
                depth={depth + 1}
                expandedFolders={expandedFolders}
                folderContents={folderContents}
                toggleFolder={toggleFolder}
                handleDownload={handleDownload}
                handleExtractArchive={handleExtractArchive}
                handleDelete={handleDelete}
                extracting={extracting}
                extractProgress={extractProgress}
              />
            ))
          ) : (
            <div className="p-4 text-center text-gray-500 text-sm" style={{ paddingLeft: `${(depth + 1) * 1.5 + 1}rem` }}>
              📄 Empty folder
            </div>
          )}
        </div>
      )}
    </>
  );
}
