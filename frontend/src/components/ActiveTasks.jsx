import { useStore } from '../store/useStore';
import { Download, Upload, Loader2, CheckCircle, XCircle } from 'lucide-react';

export default function ActiveTasks() {
  const { activeTransfers, activeExtractions } = useStore();
  
  const transfers = Object.entries(activeTransfers);
  const extractions = Object.entries(activeExtractions);
  
  if (transfers.length === 0 && extractions.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Active Tasks</h2>
      
      <div className="space-y-3">
        {transfers.map(([id, transfer]) => (
          <div key={id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {transfer.status === 'completed' ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : transfer.status === 'failed' ? (
                  <XCircle className="w-5 h-5 text-red-500" />
                ) : (
                  <Upload className="w-5 h-5 text-blue-500" />
                )}
                <span className="text-sm font-medium text-gray-900">{transfer.fileName}</span>
              </div>
              <span className="text-xs text-gray-500 capitalize">{transfer.status}</span>
            </div>
            {transfer.status === 'uploading' && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${transfer.progress || 0}%` }}
                />
              </div>
            )}
          </div>
        ))}

        {extractions.map(([id, extraction]) => (
          <div key={id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {extraction.status === 'completed' ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : extraction.status === 'failed' ? (
                  <XCircle className="w-5 h-5 text-red-500" />
                ) : (
                  <Download className="w-5 h-5 text-purple-500" />
                )}
                <span className="text-sm font-medium text-gray-900">{extraction.fileName || 'Extracting...'}</span>
              </div>
              <span className="text-xs text-gray-500 capitalize">{extraction.status}</span>
            </div>
            {extraction.status === 'extracting' && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${extraction.progress || 0}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
