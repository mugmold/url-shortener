import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Link as LinkIcon, LogOut, Settings, LayoutDashboard, ChevronDown } from 'lucide-react';

const Navbar = () => {
    const { isAuthenticated, user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <div className="navbar bg-base-100 shadow-sm px-4 sm:px-8 border-b border-base-300">
            <div className="flex-1">
                <Link to="/" className="inline-flex items-center gap-2">
                    <LinkIcon className="w-6 h-6 text-primary" />
                    <span className="text-xl font-bold">URL Shortener</span>
                </Link>
            </div>
            
            <div className="flex-none">
                {!isAuthenticated ? (
                    <div className="flex gap-2">
                        <Link to="/login" className="btn btn-ghost">Login</Link>
                        <Link to="/register" className="btn btn-primary">Get Started</Link>
                    </div>
                ) : (
                    <details className="dropdown dropdown-end">
                        <summary className="btn btn-ghost font-semibold flex items-center gap-1 cursor-pointer list-none">
                            {user?.username} <ChevronDown className="w-4 h-4 text-base-content/60" />
                        </summary>
                        
                        <ul className="dropdown-content menu bg-base-100 rounded-box w-52 p-2 shadow border border-base-300">
                            <li className="menu-title px-4 py-2">
                                <span className="text-xs text-base-content/60 block truncate select-text">
                                    {user?.email}
                                </span>
                            </li>
                            <li>
                                <Link to="/dashboard" className="flex gap-2">
                                    <LayoutDashboard className="w-4 h-4" /> Dashboard
                                </Link>
                            </li>
                            <li>
                                <Link to="/settings" className="flex gap-2">
                                    <Settings className="w-4 h-4" /> Settings
                                </Link>
                            </li>
                            <li>
                                <button onClick={handleLogout} className="flex gap-2 text-error">
                                    <LogOut className="w-4 h-4" /> Logout
                                </button>
                            </li>
                        </ul>
                    </details>
                )}
            </div>
        </div>
    );
};

export default Navbar;