import { useEffect } from 'react';
import { useParams } from 'react-router-dom';

const RedirectHandler = () => {
    const { shortCode } = useParams();

    useEffect(() => {
        const API_URL = import.meta.env.VITE_API_URL;

        window.location.replace(`${API_URL}/${shortCode}`);
    }, [shortCode]);

    return (
        <div className="flex justify-center items-center min-h-screen">
            <span className="loading loading-spinner loading-lg text-primary"></span>
        </div>
    );
};

export default RedirectHandler;