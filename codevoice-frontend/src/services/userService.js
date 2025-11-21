import axios from 'axios';
import config from '../config/api';

const CURRENT_USER_KEY = 'currentUser';

export const userService = {
    register: async (userData) => {
        const res = await axios.post(`${config.API_URL}${config.ENDPOINTS.REGISTER}`, {
            name: userData.name,
            email: userData.email,
            password: userData.password
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return res.data.user || res.data; // Handle both {user: ...} and direct user data
    },

    login: async (email, password) => {
        const res = await axios.post(`${config.API_URL}${config.ENDPOINTS.LOGIN}`, {
            email: email,
            password: password
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const user = res.data.user || res.data; // Handle both {user: ...} and direct user data
        localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
        return user;
    },

    logout: () => {
        localStorage.removeItem(CURRENT_USER_KEY);
    },

    getCurrentUser: () => {
        const user = localStorage.getItem(CURRENT_USER_KEY);
        return user ? JSON.parse(user) : null;
    },

    getUser: async (userId) => {
        const res = await axios.get(`${config.API_URL}${config.ENDPOINTS.GET_USER}${userId}`);
        return res.data;
    },

    updateProfile: async (userId, profileData) => {
        const res = await axios.put(`${config.API_URL}${config.ENDPOINTS.GET_USER}${userId}`, profileData);
        
        // Extract user data from backend response {message, user}
        const userData = res.data.user || res.data;
        
        // also update local copy
        const current = JSON.parse(localStorage.getItem(CURRENT_USER_KEY) || '{}');
        if (current?.id === userId) {
            localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userData));
        }
        return userData;
    }
};