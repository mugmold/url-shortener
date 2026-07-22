import { createContext, useState, useEffect, useContext } from 'react';
import apiClient from '../api/client';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    // check if user is already logged in when the app loads
    useEffect(() => {
        if (window.location.pathname === '/too-many-requests') {
            setLoading(false);
            return;
        }

        const checkUser = async () => {
            try {
                const response = await apiClient.get('/users/me');
                setUser(response.data);
                setIsAuthenticated(true);
            } catch (err) {
                if (err.response?.status === 401) {
                    logout();
                }
            } finally {
                setLoading(false);
            }
        };

        const token = localStorage.getItem('access_token');
        if (token) {
            checkUser();
        } else {
            setLoading(false);
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

        const userResponse = await apiClient.get('/users/me');
        setUser(userResponse.data);
        setIsAuthenticated(true);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);