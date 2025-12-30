import { useState } from 'react';
import { Link, Upload, Loader2 } from 'lucide-react';
import { fileAPI } from '../api/client';
import { useStore } from '../store/useStore';

export default function TransferPanel() {
  const [driveUrl, setDriveUrl] = useState('');
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const { refreshFiles } = useStore();

  const handleTransfer = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await fileAPI.transferFile(driveUrl, fileName || null);
      setResult(data);
      setDriveUrl('');
      setFileName('');
      
      // Refresh file list after successful transfer
      setTimeout(() => refreshFiles(), 1000);
    } catch (err) {
      setError(err.response?.data?.error || 'Transfer failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="bg-gradient-to-br from-green-500 to-emerald-600 p-2 rounded-lg">
          <Link className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Transfer from Drive Link</h2>
      </div>

      <form onSubmit={handleTransfer} className="space-y-4">
        <div>
          <label htmlFor="driveUrl" className="block text-sm font-medium text-gray-700 mb-2">
            Google Drive Share Link
          </label>
          <input
            id="driveUrl"
            type="url"
            value={driveUrl}
            onChange={(e) => setDriveUrl(e.target.value)}
            placeholder="https://drive.google.com/file/d/..."
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
          />
        </div>

        <div>
          <label htmlFor="fileName" className="block text-sm font-medium text-gray-700 mb-2">
            Custom File Name (Optional)
          </label>
          <input
            id="fileName"
            type="text"
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
            placeholder="Leave empty to use original name"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Transferring...
            </>
          ) : (
            <>
              <Upload className="w-5 h-5 mr-2" />
              Transfer to My Drive
            </>
          )}
        </button>
      </form>

      {result && (
        <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-green-900 mb-2">✓ Transfer Successful!</h3>
          <div className="text-sm text-green-700 space-y-1">
            <p><strong>File:</strong> {result.fileName}</p>
            <p><strong>Size:</strong> {result.fileSize}</p>
            <p><strong>Time:</strong> {result.transferTime}</p>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-red-900 mb-1">✗ Transfer Failed</h3>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
}
