import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/client';
import { Eye, EyeOff } from 'lucide-react';

const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const usernameRegex = /^[a-zA-Z0-9_]+$/;
        if (!usernameRegex.test(username)) {
            setError('Username can only contain letters, numbers, and underscores.');
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        setIsLoading(true);

        try {
            await apiClient.post('/auth/register', {
                username,
                email,
                password,
                confirm_password: confirmPassword
            });
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to register. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-base-200 p-4">
            <div className="card w-full max-w-md bg-base-100 shadow-xl border border-base-300">
                <div className="card-body">
                    <h2 className="card-title text-2xl font-bold justify-center mb-4">Create an Account</h2>

                    {error && (
                        <div className="alert alert-error text-sm rounded-lg py-2">
                            <span>{error}</span>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="form-control">
                            <label className="label">
                                <span className="label-text font-semibold">Username</span>
                            </label>
                            <input
                                type="text"
                                placeholder="Choose a username (3-20 chars)"
                                className="input input-bordered w-full"
                                value={username}
                                onChange={(e) => setUsername(e.target.value.toLowerCase())}
                                required
                                minLength={3}
                                maxLength={20}
                                pattern="^[a-zA-Z0-9_]+$"
                                title="Only letters, numbers, and underscores are allowed"
                            />
                            <label className="label py-1">
                                <span className="label-text-alt text-base-content/60">No spaces, dashes, or special characters</span>
                            </label>
                        </div>

                        <div className="form-control">
                            <label className="label">
                                <span className="label-text font-semibold">Email</span>
                            </label>
                            <input
                                type="email"
                                placeholder="Enter your email"
                                className="input input-bordered w-full"
                                value={email}
                                onChange={(e) => setEmail(e.target.value.toLowerCase())}
                                required
                            />
                        </div>

                        <div className="form-control">
                            <label className="label">
                                <span className="label-text font-semibold">Password</span>
                            </label>
                            <div className="relative">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    placeholder="Create a password (min 8 chars)"
                                    className="input input-bordered w-full pr-10"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    minLength={8}
                                />
                                <button
                                    type="button"
                                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-base-content/60 hover:text-base-content"
                                    onClick={() => setShowPassword(!showPassword)}
                                    tabIndex={-1}
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        <div className="form-control">
                            <label className="label">
                                <span className="label-text font-semibold">Confirm Password</span>
                            </label>
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="Confirm your password"
                                className="input input-bordered w-full"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                minLength={8}
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary w-full mt-4"
                            disabled={isLoading}
                        >
                            {isLoading ? <span className="loading loading-spinner"></span> : 'Register'}
                        </button>
                    </form>

                    <div className="divider">OR</div>

                    <div className="text-center text-sm">
                        <p>Already have an account? <Link to="/login" className="link link-primary font-semibold">Login here</Link></p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;