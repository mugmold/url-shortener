import { Link } from 'react-router-dom';
import { FileQuestion, Home } from 'lucide-react';

const NotFound = () => {
    return (
        <div className="flex flex-col min-h-[calc(100vh-4rem)] items-center justify-center p-4">
            <div className="text-center max-w-md">
                <div className="flex justify-center mb-6">
                    <div className="p-6 bg-base-200 rounded-full border border-base-300">
                        <FileQuestion className="w-20 h-20 text-primary" />
                    </div>
                </div>

                <h1 className="text-7xl font-bold mb-4 text-base-content">404</h1>
                <h2 className="text-2xl font-semibold mb-4">Page Not Found</h2>

                <p className="text-base-content/70 mb-8">
                    Oops! The page you're looking for doesn't exist, has been moved, or is just a really stupid URL.
                </p>

                <Link to="/" className="btn btn-primary">
                    <Home className="w-5 h-5 mr-2" />
                    Back to Home
                </Link>
            </div>
        </div>
    );
};

export default NotFound;