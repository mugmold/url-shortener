import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Link as LinkIcon, Zap, Edit3, LayoutDashboard as LayoutIcon, ArrowRight } from 'lucide-react';

const Home = () => {
    const { isAuthenticated } = useAuth();

    return (
        <div className="flex flex-col min-h-[calc(100vh-4rem)]">
            <div className="hero bg-base-200 flex-1">
                <div className="hero-content text-center px-4 py-20">
                    <div className="max-w-3xl">
                        <div className="flex justify-center mb-6">
                            <div className="p-4 bg-primary/10 rounded-full">
                                <LinkIcon className="w-16 h-16 text-primary" />
                            </div>
                        </div>
                        <h1 className="text-5xl sm:text-6xl font-bold mb-8">
                            Shorten Your Links. <br className="hidden sm:block" />
                            <span className="text-primary">Keep It Simple.</span>
                        </h1>
                        <p className="text-lg sm:text-xl text-base-content/70 mb-10 max-w-2xl mx-auto">
                            Turn long, messy URLs into clean, manageable links with custom aliases.
                        </p>

                        <div className="flex flex-col sm:flex-row justify-center gap-4">
                            {isAuthenticated ? (
                                <Link to="/dashboard" className="btn btn-primary btn-lg">
                                    Go to Dashboard <ArrowRight className="w-5 h-5" />
                                </Link>
                            ) : (
                                <>
                                    <Link to="/register" className="btn btn-primary btn-lg">
                                        Get Started
                                    </Link>
                                    <Link to="/login" className="btn btn-outline btn-lg">
                                        Login
                                    </Link>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-base-100 py-24 px-4 sm:px-8">
                <div className="max-w-7xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="card bg-base-200 border border-base-300">
                            <div className="card-body items-center text-center">
                                <Zap className="w-8 h-8 text-primary mb-2" />
                                <h3 className="card-title">Instant Shortening</h3>
                                <p className="text-base-content/70 text-sm">Paste any long URL and instantly get a clean, short link ready to share.</p>
                            </div>
                        </div>
                        <div className="card bg-base-200 border border-base-300">
                            <div className="card-body items-center text-center">
                                <Edit3 className="w-8 h-8 text-primary mb-2" />
                                <h3 className="card-title">Custom Aliases</h3>
                                <p className="text-base-content/70 text-sm">Ditch the random characters. Make your links readable by choosing your own custom alias.</p>
                            </div>
                        </div>
                        <div className="card bg-base-200 border border-base-300">
                            <div className="card-body items-center text-center">
                                <LayoutIcon className="w-8 h-8 text-primary mb-2" />
                                <h3 className="card-title">Link Management</h3>
                                <p className="text-base-content/70 text-sm">View, edit, and delete all of your shortened links from a simple dashboard.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;