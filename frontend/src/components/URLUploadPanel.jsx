import { useState } from 'react';
import { ExternalLink, Upload, Loader2 } from 'lucide-react';
import { fileAPI } from '../api/client';
import { useStore } from '../store/useStore';

export default function URLUploadPanel() {
  const [downloadUrl, setDownloadUrl] = useState('');
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const { addTransfer, updateTransfer, removeTransfer, refreshFiles } = useStore();

  const handleUpload = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setProgress(null);

    const taskId = `upload-${Date.now()}`;
    
    try {
      // Add to active transfers
      addTransfer(taskId, {
        type: 'url-upload',
        url: downloadUrl,
        fileName: fileName || 'Unknown',
        status: 'starting',
        progress: 0,
      });

      // Start upload
      const result = await fileAPI.uploadFromUrl(downloadUrl, fileName || null);
      
      updateTransfer(taskId, {
        status: 'completed',
        progress: 100,
        result,
      });

      setProgress(result);
      setDownloadUrl('');
      setFileName('');
      
      // Refresh file list
      setTimeout(() => {
        refreshFiles();
        removeTransfer(taskId);
      }, 2000);
      
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
      updateTransfer(taskId, {
        status: 'failed',
        error: err.message,
      });
      setTimeout(() => removeTransfer(taskId), 3000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-cyan-600 p-2 rounded-lg">
          <ExternalLink className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Upload from Direct Link</h2>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <p className="text-sm text-yellow-800">
          <strong>⚠️ Note:</strong> URL upload requires a backend server and is not available in the client-side only version. 
          Please use browser extensions or download files manually to upload to Google Drive.
        </p>
      </div>

      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <label htmlFor="downloadUrl" className="block text-sm font-medium text-gray-700 mb-2">
            Direct Download URL
          </label>
          <input
            id="downloadUrl"
            type="url"
            value={downloadUrl}
            onChange={(e) => setDownloadUrl(e.target.value)}
            placeholder="https://example.com/file.zip"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          />
        </div>

        <div>
          <label htmlFor="fileNameUpload" className="block text-sm font-medium text-gray-700 mb-2">
            Custom File Name (Optional)
          </label>
          <input
            id="fileNameUpload"
            type="text"
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
            placeholder="my-file.zip"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          />
        </div>

        <button
          type="submtrue}
          className="w-full bg-gray-400 text-white py-3 px-4 rounded-lg font-semibold cursor-not-allowed flex items-center justify-center opacity-50
          className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-blue-700 hover:to-cyan-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="w-5 h-5 mr-2" />
              Upload to My Drive
            </>
          )}
        </button>
      </form>

      {progress && (
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">✓ Upload Successful!</h3>
          <div className="text-sm text-blue-700 space-y-1">
            <p><strong>File:</strong> {progress.fileName}</p>
            {progress.fileSize && <p><strong>Size:</strong> {progress.fileSize}</p>}
            {progress.uploadTime && <p><strong>Time:</strong> {progress.uploadTime}</p>}
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-red-900 mb-1">✗ Upload Failed</h3>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
}
