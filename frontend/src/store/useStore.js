import { create } from 'zustand';
import { fileAPI } from '../api/client';

export const useStore = create((set, get) => ({
  // Authentication
  isAuthenticated: false,
  user: null,
  setAuth: (isAuthenticated, user = null) => set({ isAuthenticated, user }),
  
  // Files
  files: [],
  loading: false,
  error: null,
  nextPageToken: null,
  
  setFiles: (files) => set({ files }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  // Fetch files from Google Drive
  fetchFiles: async (pageToken = null) => {
    set({ loading: true, error: null });
    try {
      const data = await fileAPI.listFiles(pageToken);
      set({
        files: pageToken ? [...get().files, ...data.files] : data.files,
        nextPageToken: data.nextPageToken,
        loading: false,
      });
    } catch (error) {
      set({
        error: error.response?.data?.error || error.message,
        loading: false,
      });
    }
  },
  
  // Refresh file list
  refreshFiles: async () => {
    set({ files: [], nextPageToken: null });
    await get().fetchFiles();
  },
  
  // Active transfers
  activeTransfers: {},
  
  addTransfer: (id, data) => set((state) => ({
    activeTransfers: {
      ...state.activeTransfers,
      [id]: data,
    },
  })),
  
  updateTransfer: (id, updates) => set((state) => ({
    activeTransfers: {
      ...state.activeTransfers,
      [id]: {
        ...state.activeTransfers[id],
        ...updates,
      },
    },
  })),
  
  removeTransfer: (id) => set((state) => {
    const newTransfers = { ...state.activeTransfers };
    delete newTransfers[id];
    return { activeTransfers: newTransfers };
  }),
  
  // Active extractions
  activeExtractions: {},
  
  addExtraction: (taskId, data) => set((state) => ({
    activeExtractions: {
      ...state.activeExtractions,
      [taskId]: data,
    },
  })),
  
  updateExtraction: (taskId, updates) => set((state) => ({
    activeExtractions: {
      ...state.activeExtractions,
      [taskId]: {
        ...state.activeExtractions[taskId],
        ...updates,
      },
    },
  })),
  
  removeExtraction: (taskId) => set((state) => {
    const newExtractions = { ...state.activeExtractions };
    delete newExtractions[taskId];
    return { activeExtractions: newExtractions };
  }),
  
  // Selected files
  selectedFiles: [],
  
  toggleFileSelection: (fileId) => set((state) => {
    const isSelected = state.selectedFiles.includes(fileId);
    return {
      selectedFiles: isSelected
        ? state.selectedFiles.filter(id => id !== fileId)
        : [...state.selectedFiles, fileId],
    };
  }),
  
  clearSelection: () => set({ selectedFiles: [] }),
  
  selectAll: () => set((state) => ({
    selectedFiles: state.files.map(f => f.id),
  })),
}));
