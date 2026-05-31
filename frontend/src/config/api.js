import axios from 'axios';

const ENV_API_URL = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace(/\/+$/, '') : '';
const API_BASE = ENV_API_URL 
    ? (ENV_API_URL.endsWith('/api') ? ENV_API_URL : `${ENV_API_URL}/api`)
    : 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json'
    }
});

export default apiClient;
