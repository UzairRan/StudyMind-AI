import axios from 'axios';
import config from '../config';

const api = axios.create({
    baseURL: config.API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add response interceptor for error handling
api.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// API functions
export const uploadPDFs = async (files) => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    const response = await api.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const queryDocuments = async (query, chapterFilter = null, modelName = 'gemini-1.5-flash') => {
    const response = await api.post('/query', {
        query,
        chapter_filter: chapterFilter,
        model_name: modelName
    });
    return response.data;
};

export const generateQuiz = async (chapter, numQuestions = 5) => {
    const response = await api.post('/generate-quiz', {
        chapter,
        num_questions: numQuestions
    });
    return response.data;
};

export const getChapters = async () => {
    const response = await api.get('/chapters');
    return response.data;
};

export const getModels = async () => {
    const response = await api.get('/models');
    return response.data;
};

export const clearAllData = async () => {
    const response = await api.delete('/clear');
    return response.data;
};

export const healthCheck = async () => {
    const response = await api.get('/health');
    return response.data;
};

export default api; 