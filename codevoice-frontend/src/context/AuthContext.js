import React, { createContext, useState, useContext, useEffect } from 'react';
import { userService } from '../services/userService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is logged in
        const currentUser = userService.getCurrentUser();
        setUser(currentUser);
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const userData = await userService.login(email, password);
        setUser(userData);
        return userData;
    };

    const logout = () => {
        userService.logout();
        setUser(null);
    };

    const register = async (userData) => {
        await userService.register(userData);
    };

    const updateProfile = async (userId, profileData) => {
        const updatedUser = await userService.updateProfile(userId, profileData);
        setUser(updatedUser);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <AuthContext.Provider value={{ user, login, logout, register, updateProfile }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);