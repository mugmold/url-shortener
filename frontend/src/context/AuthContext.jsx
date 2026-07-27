import { createContext, useState, useEffect, useContext } from 'react';
import apiClient from '../api/client';
import axios from 'axios';

const AuthContext = createContext();

const decodeJwt = (token) => {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
};

export const AuthProvider = ({ children }) => {
    // check access_token from localStorage
    const [user, setUser] = useState(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            const decoded = decodeJwt(token);
            if (decoded) {
                // check if the token is expired right now
                const currentTime = Date.now() / 1000;
                if (decoded.exp < currentTime) {
                    return null; // token is expired, act like we don't have a user yet
                }
                return { id: decoded.sub, username: decoded.username, email: decoded.email };
            }
        }
        return null;
    });

    const [isAuthenticated, setIsAuthenticated] = useState(() => !!user);

    // only show loading if access_token is dead but refresh_token exists
    const [loading, setLoading] = useState(() => {
        const hasRefreshToken = !!localStorage.getItem('refresh_token');
        return !user && hasRefreshToken;
    });

    const refreshUserToken = async () => {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh`, {
                refresh_token: refreshToken
            });
            const { access_token, refresh_token: new_refresh } = response.data;

            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', new_refresh);

            const decoded = decodeJwt(access_token);
            setUser({ id: decoded.sub, username: decoded.username, email: decoded.email });
            setIsAuthenticated(true);
            return true;
        } catch (error) {
            logout();
            return false;
        }
    };

    useEffect(() => {
        if (loading) {
            // refresh the token, then turn off the loading spinner
            refreshUserToken().finally(() => setLoading(false));
        }
    }, []);

    const login = async (usernameOrEmail, password) => {
        const formData = new URLSearchParams();
        formData.append('username', usernameOrEmail);
        formData.append('password', password);

        const response = await apiClient.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        const decoded = decodeJwt(access_token);
        setUser({ id: decoded.sub, username: decoded.username, email: decoded.email });
        setIsAuthenticated(true);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, loading, login, logout, refreshUserToken }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);