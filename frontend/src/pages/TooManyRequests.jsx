import { Link } from 'react-router-dom';
import { AlertTriangle, ArrowLeft } from 'lucide-react';

const TooManyRequests = () => {
    return (
        <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-base-200 p-4">
            <div className="card w-full max-w-md bg-base-100 shadow-xl border border-base-300 text-center">
                <div className="card-body items-center p-8">
                    <div className="p-4 bg-warning/10 rounded-full text-warning mb-4">
                        <AlertTriangle className="w-12 h-12" />
                    </div>

                    <h2 className="card-title text-2xl font-bold mb-2">Whoa, slow down!</h2>

                    <p className="text-base-content/70 text-sm mb-6">
                        You've been making too many requests in a short amount of time. Please wait a minute before trying again.
                    </p>

                    <Link to="/" className="btn btn-primary w-full gap-2">
                        <ArrowLeft className="w-4 h-4" /> Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default TooManyRequests;