import { useState, useEffect } from 'react';
import { useStore } from './store/useStore';
import { authAPI } from './api/client';
import Login from './components/Login';
import Header from './components/Header';
import TransferPanel from './components/TransferPanel';
import URLUploadPanel from './components/URLUploadPanel';
import FileList from './components/FileList';
import ActiveTasks from './components/ActiveTasks';

function App() {
  const { isAuthenticated, setAuth } = useStore();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    // Check authentication
    const checkAuth = async () => {
      try {
        await authAPI.checkAuth();
        setAuth(true);
      } catch (error) {
        setAuth(false);
      } finally {
        setChecking(false);
      }
    };

    checkAuth();
  }, [setAuth]);

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-white border-t-transparent mb-4"></div>
          <p className="text-white text-lg font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <TransferPanel />
          <URLUploadPanel />
        </div>

        <div className="mb-6">
          <ActiveTasks />
        </div>

        <FileList />
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>Google Drive Transfer Pro - Secure & Fast File Management</p>
            <p className="mt-1">Built with React + Vite + Flask</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
