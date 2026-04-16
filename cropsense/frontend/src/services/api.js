import axios from 'axios';

const API_BASE_URL = window.location.origin.includes('localhost') 
    ? 'http://127.0.0.1:8000/api' 
    : '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const diseaseService = {
    predict: async (imageFile) => {
        const formData = new FormData();
        formData.append('file', imageFile);
        const response = await api.post('/disease/predict', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
};

export const yieldService = {
    predict: async (data) => {
        const response = await api.post('/yield/predict', data);
        return response.data;
    },
};

export const healthService = {
    check: async () => {
        const response = await axios.get('http://127.0.0.1:8000/health');
        return response.data;
    },
};

export default api;
