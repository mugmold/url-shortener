import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';
import { AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';

const Settings = () => {
    const { user } = useAuth();

    const [username, setUsername] = useState(user?.username || '');
    const [email, setEmail] = useState(user?.email || '');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const [status, setStatus] = useState({ type: '', message: '' });
    const [isSaving, setIsSaving] = useState(false);

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        setStatus({ type: '', message: '' });

        if (password && password !== confirmPassword) {
            setStatus({ type: 'error', message: 'New passwords do not match.' });
            return;
        }

        setIsSaving(true);

        const updateData = {};
        if (username !== user?.username) updateData.username = username;
        if (email !== user?.email) updateData.email = email;
        if (password) {
            updateData.password = password;
            updateData.confirm_password = confirmPassword;
        }

        if (Object.keys(updateData).length === 0) {
            setStatus({ type: 'info', message: 'No changes made.' });
            setIsSaving(false);
            return;
        }

        try {
            await apiClient.patch('/users/me', updateData);
            setStatus({ type: 'success', message: 'Profile updated successfully!' });
            setPassword('');
            setConfirmPassword('');
        } catch (error) {
            setStatus({
                type: 'error',
                message: error.response?.data?.detail || 'Failed to update profile.'
            });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-base-200 p-4">
            <div className="card w-full max-w-md bg-base-100 shadow-xl border border-base-300">
                <div className="card-body">
                    <h2 className="card-title text-2xl font-bold justify-center mb-2">Profile Settings</h2>
                    <p className="text-center text-base-content/70 text-sm mb-4">Update your account details and password.</p>

                    {status.message && (
                        <div className={`alert ${status.type === 'success' ? 'alert-success' : status.type === 'error' ? 'alert-error' : 'alert-info'} text-sm rounded-lg py-2 mb-2`}>
                            {status.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                            <span>{status.message}</span>
                        </div>
                    )}

                    <form onSubmit={handleUpdateProfile} className="space-y-4">
                        <div className="form-control">
                            <label className="label"><span className="label-text font-semibold">Username</span></label>
                            <input
                                type="text"
                                className="input input-bordered w-full"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>

                        <div className="form-control">
                            <label className="label"><span className="label-text font-semibold">Email Address</span></label>
                            <input
                                type="email"
                                className="input input-bordered w-full"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="divider text-xs text-base-content/50">CHANGE PASSWORD</div>

                        <div className="form-control">
                            <label className="label">
                                <span className="label-text font-semibold">New Password</span>
                                <span className="label-text-alt text-base-content/60">Optional</span>
                            </label>
                            <div className="relative">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    className="input input-bordered w-full pr-10"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
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
                                <span className="label-text font-semibold">Confirm New Password</span>
                            </label>
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="••••••••"
                                className="input input-bordered w-full"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                minLength={8}
                                disabled={!password}
                            />
                        </div>

                        <button type="submit" className="btn btn-primary w-full mt-4" disabled={isSaving}>
                            {isSaving ? <span className="loading loading-spinner"></span> : 'Save Changes'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Settings;