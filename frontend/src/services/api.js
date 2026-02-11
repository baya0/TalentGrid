// frontend/src/services/api.js
/**
 * TalentGrid API Service
 *
 * This module provides a clean interface for all API calls to the backend.
 * Import and use these functions in your React components.
 *
 * Example:
 *   import { login, getCandidates, searchCandidates } from '../services/api';
 */

import axios from 'axios';

// ============================================================================
// API CONFIGURATION
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If 401 Unauthorized, clear token and redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// AUTHENTICATION ENDPOINTS
// ============================================================================

/**
 * Register a new user
 * @param {Object} userData - { email, password, full_name, company }
 * @returns {Promise<Object>} Created user data
 */
export const register = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

/**
 * Login and get JWT token
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} { access_token, token_type }
 */
export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });

  // Store token in localStorage
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }

  return response.data;
};

/**
 * Get current logged-in user info
 * @returns {Promise<Object>} User data
 */
export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

/**
 * Logout - clear stored credentials
 */
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

// ============================================================================
// CANDIDATE ENDPOINTS
// ============================================================================

/**
 * Get all candidates (paginated)
 * @param {number} skip - Number of records to skip (default: 0)
 * @param {number} limit - Max records to return (default: 50)
 * @returns {Promise<Array>} List of candidates
 */
export const getCandidates = async (skip = 0, limit = 50) => {
  const response = await api.get('/candidates', {
    params: { skip, limit },
  });
  return response.data;
};

/**
 * Get a single candidate by ID
 * @param {number} id - Candidate ID
 * @returns {Promise<Object>} Candidate data
 */
export const getCandidate = async (id) => {
  const response = await api.get(`/candidates/${id}`);
  return response.data;
};

/**
 * Create a new candidate
 * @param {Object} candidateData - Candidate information
 * @returns {Promise<Object>} Created candidate
 */
export const createCandidate = async (candidateData) => {
  const response = await api.post('/candidates', candidateData);
  return response.data;
};

/**
 * Update an existing candidate
 * @param {number} id - Candidate ID
 * @param {Object} candidateData - Updated candidate information
 * @returns {Promise<Object>} Updated candidate
 */
export const updateCandidate = async (id, candidateData) => {
  const response = await api.put(`/candidates/${id}`, candidateData);
  return response.data;
};

/**
 * Delete a candidate
 * @param {number} id - Candidate ID
 * @returns {Promise<void>}
 */
export const deleteCandidate = async (id) => {
  await api.delete(`/candidates/${id}`);
};

// ============================================================================
// SEARCH ENDPOINTS
// ============================================================================

/**
 * Search candidates using RAG-powered semantic search
 * @param {string} query - Natural language search query
 * @param {Object} options - Search options
 * @param {number} options.top_k - Number of results (default: 10)
 * @param {Object} options.filters - Optional filters
 * @returns {Promise<Object>} { results, total_count, query }
 */
export const searchCandidates = async (query, options = {}) => {
  const { top_k = 10, filters = {} } = options;

  const response = await api.post('/search', {
    query,
    top_k,
    filters,
  });
  return response.data;
};

/**
 * Get all candidates (without search query)
 * @param {number} limit - Max results (default: 20)
 * @returns {Promise<Object>} { candidates, total_results, query }
 */
export const getAllCandidatesForSearch = async (limit = 20) => {
  const response = await api.get('/search/all', { params: { limit } });
  return response.data;
};

// ============================================================================
// CV IMPORT ENDPOINTS
// ============================================================================

/**
 * Upload a CV file for parsing
 * @param {File} file - CV file (PDF or DOCX)
 * @param {Function} onProgress - Progress callback (0-100)
 * @returns {Promise<Object>} Parsed candidate data
 */
export const uploadCV = async (file, onProgress = null) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/import/cv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percent);
      }
    },
  });

  return response.data;
};

/**
 * Check the status of a CV upload
 * @param {number} fileId - File ID from upload response
 * @returns {Promise<Object>} { file_id, filename, status, candidate_id, parsed_data }
 */
export const getUploadStatus = async (fileId) => {
  const response = await api.get(`/import/status/${fileId}`);
  return response.data;
};

/**
 * Upload multiple CV files
 * @param {File[]} files - Array of CV files
 * @param {Function} onProgress - Progress callback for each file
 * @returns {Promise<Array>} Array of upload results
 */
export const uploadMultipleCVs = async (files, onProgress = null) => {
  const results = [];

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    try {
      const result = await uploadCV(file, (percent) => {
        if (onProgress) {
          onProgress(i, file.name, percent);
        }
      });
      results.push({ file: file.name, success: true, data: result });
    } catch (error) {
      results.push({ file: file.name, success: false, error: error.message });
    }
  }

  return results;
};

// ============================================================================
// GMAIL IMPORT ENDPOINTS
// ============================================================================

/**
 * Get Gmail OAuth URL to initiate connection
 * @returns {Promise<Object>} { auth_url, state }
 */
export const getGmailAuthUrl = async () => {
  const response = await api.get('/gmail/auth');
  return response.data;
};

/**
 * Exchange OAuth code for tokens
 * @param {string} code - Authorization code from Google
 * @param {string} state - State parameter for security
 * @returns {Promise<Object>} { success, message }
 */
export const exchangeGmailToken = async (code, state) => {
  const response = await api.post('/gmail/callback', { code, state });
  return response.data;
};

/**
 * Check Gmail connection status
 * @returns {Promise<Object>} { connected: boolean }
 */
export const getGmailStatus = async () => {
  const response = await api.get('/gmail/status');
  return response.data;
};

/**
 * Scan Gmail for CV attachments
 * @param {Object} tokens - OAuth tokens
 * @param {Object} options - Scan options
 * @returns {Promise<Object>} { emails, total_cvs }
 */
export const scanGmailForCVs = async (tokens, options = {}) => {
  const response = await api.post('/gmail/scan', {
    tokens,
    max_results: options.maxResults || 50,
    days_back: options.daysBack || 30
  });
  return response.data;
};

/**
 * Import a specific CV from Gmail
 * @param {Object} tokens - OAuth tokens
 * @param {string} messageId - Email message ID
 * @param {string} attachmentId - Attachment ID
 * @param {string} filename - Filename
 * @returns {Promise<Object>} Import result
 */
export const importCVFromGmail = async (tokens, messageId, attachmentId, filename) => {
  const response = await api.post('/gmail/import', {
    tokens,
    message_id: messageId,
    attachment_id: attachmentId,
    filename
  });
  return response.data;
};

/**
 * Disconnect Gmail account
 * @returns {Promise<Object>} { success, message }
 */
export const disconnectGmail = async () => {
  const response = await api.delete('/gmail/disconnect');
  return response.data;
};

// ============================================================================
// ANALYTICS ENDPOINTS (if implemented)
// ============================================================================

/**
 * Get dashboard statistics
 * @returns {Promise<Object>} Dashboard stats
 */
export const getDashboardStats = async () => {
  const response = await api.get('/analytics/dashboard');
  return response.data;
};

/**
 * Get candidate analytics
 * @returns {Promise<Object>} Analytics data
 */
export const getAnalytics = async () => {
  const response = await api.get('/analytics');
  return response.data;
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

/**
 * Get stored auth token
 * @returns {string|null}
 */
export const getToken = () => {
  return localStorage.getItem('token');
};

/**
 * Health check - verify backend is running
 * @returns {Promise<Object>} { status: "healthy" }
 */
export const healthCheck = async () => {
  const response = await axios.get(`${API_BASE_URL.replace('/api', '')}/health`);
  return response.data;
};

// Export the axios instance for custom requests
export default api;
