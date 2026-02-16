import axios from 'axios';
import { auth } from '../config/firebase';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptor for Bearer token
api.interceptors.request.use(
  async (config) => {
    const firebaseToken = await auth.currentUser?.getIdToken();
    const token = firebaseToken || localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      localStorage.setItem('token', token);
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Add interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear only the local cache. Firebase session state is handled in AuthContext.
      localStorage.removeItem('token');
    }
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  },
);

// Auth Functions
export const login = async () => {
  throw new Error('Backend JWT login disabled. Use Firebase Auth login flow.');
};

export const register = async () => {
  throw new Error('Backend register disabled. Use Firebase Auth signup flow.');
};

export const getCurrentUser = async () => {
  const response = await api.get('/api/v1/auth/me');
  return response.data;
};

export const listUsers = async () => {
  const response = await api.get('/api/v1/admin/users');
  return response.data;
};

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/v1/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const listDocuments = async () => {
  const response = await api.get('/api/v1/documents');
  return response.data;
};

export const deleteDocument = async (id: string) => {
  const response = await api.delete(`/api/v1/documents/${id}`);
  return response.data;
};

export const queryRAG = async (
  question: string,
  documentIds?: string[],
  conversationId?: string,
) => {
  const response = await api.post('/api/v1/query', {
    question,
    document_ids: documentIds,
    conversation_id: conversationId,
  });
  return response.data;
};

export const createConversation = async (title?: string) => {
  const response = await api.post('/api/v1/conversations', { title });
  return response.data;
};

export const listConversations = async (q?: string) => {
  const response = await api.get('/api/v1/conversations', {
    params: q ? { q } : undefined,
  });
  return response.data;
};

export const getConversationHistory = async (conversationId: string) => {
  const response = await api.get(`/api/v1/conversations/${conversationId}`);
  return response.data;
};

export const deleteConversation = async (conversationId: string) => {
  const response = await api.delete(`/api/v1/conversations/${conversationId}`);
  return response.data;
};

export const exportConversation = async (
  conversationId: string,
  format: 'md' | 'txt' = 'md',
) => {
  const response = await api.get(
    `/api/v1/conversations/${conversationId}/export`,
    {
      params: { format },
      responseType: 'blob',
    },
  );
  return response.data;
};

export const createConversationShareLink = async (conversationId: string) => {
  const response = await api.post(
    `/api/v1/conversations/${conversationId}/share`,
  );
  return response.data;
};

export const getSharedConversation = async (token: string) => {
  const response = await api.get(`/api/v1/conversations/shared/${token}`);
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/api/v1/stats');
  return response.data;
};

export const getUsageStats = async () => {
  const response = await api.get('/api/v1/stats/usage');
  return response.data;
};

export default api;
