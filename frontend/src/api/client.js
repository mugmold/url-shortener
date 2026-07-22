import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// attach the access token to every request
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// response interceptor to catch 429 errors globally
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 429) {
            if (window.location.pathname !== '/too-many-requests') {
                window.location.href = '/too-many-requests';
            }
        }
        return Promise.reject(error);
    }
);

// catch errors and attempt to refresh the token
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // if the error is 401 Unauthorized and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                try {
                    // ask the backend for a new set of tokens using the dynamic URL
                    const response = await axios.post(`${API_URL}/auth/refresh`, {
                        refresh_token: refreshToken
                    });

                    const { access_token, refresh_token } = response.data;

                    // save the new tokens
                    localStorage.setItem('access_token', access_token);
                    localStorage.setItem('refresh_token', refresh_token);

                    // update headers and retry the original failed request
                    apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
                    originalRequest.headers['Authorization'] = `Bearer ${access_token}`;

                    return apiClient(originalRequest);
                } catch (refreshError) {
                    // if the refresh token is also expired, log the user out completely
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                }
            }
        }

        return Promise.reject(error);
    }
);

export default apiClient;