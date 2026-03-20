import axios from 'axios';

const API_V1_PATH = '/api/v1';
const AUTH_API_PATH = '/api/auth';
const defaultApiBaseUrl = `http://localhost:8000${API_V1_PATH}`;
const configuredApiBaseUrl = import.meta.env.VITE_API_URL || defaultApiBaseUrl;

const buildSiblingBaseUrl = (baseUrl: string, siblingPath: string) => {
  const normalizedBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

  if (normalizedBaseUrl.endsWith(API_V1_PATH)) {
    return `${normalizedBaseUrl.slice(0, -API_V1_PATH.length)}${siblingPath}`;
  }

  return siblingPath;
};

// Create an Axios instance with base URL mapping to the FastAPI server
const api = axios.create({
  baseURL: configuredApiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authApi = axios.create({
  baseURL: buildSiblingBaseUrl(configuredApiBaseUrl, AUTH_API_PATH),
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
