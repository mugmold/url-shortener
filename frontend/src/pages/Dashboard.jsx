import { useState, useEffect } from 'react';
import { Copy, ExternalLink, Trash2, Edit, Plus, AlertCircle } from 'lucide-react';
import apiClient from '../api/client';

const API_BASE_URL = import.meta.env.VITE_API_URL;

const Dashboard = () => {
    const [urls, setUrls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const limit = 10;

    const [newUrl, setNewUrl] = useState('');
    const [customAlias, setCustomAlias] = useState('');
    const [createError, setCreateError] = useState('');
    const [isCreating, setIsCreating] = useState(false);

    const [urlToDelete, setUrlToDelete] = useState(null);

    const [urlToEdit, setUrlToEdit] = useState(null);
    const [editUrl, setEditUrl] = useState('');
    const [editAlias, setEditAlias] = useState('');
    const [editError, setEditError] = useState('');
    const [isEditing, setIsEditing] = useState(false);

    const fetchUrls = async () => {
        setLoading(true);
        try {
            const skip = (page - 1) * limit;
            const response = await apiClient.get('/users/me/urls', {
                params: { skip, limit }
            });
            setUrls(response.data.items);
            setTotal(response.data.total);
        } catch (error) {
            console.error("Failed to fetch URLs:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUrls();
    }, [page]);

    const handleCopy = (shortenedUrl) => {
        navigator.clipboard.writeText(shortenedUrl);
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        setCreateError('');
        setIsCreating(true);

        try {
            await apiClient.post('/urls', {
                original_url: newUrl,
                custom_alias: customAlias || null,
            });

            document.getElementById('create_modal').close();
            setNewUrl('');
            setCustomAlias('');
            fetchUrls();
        } catch (error) {
            setCreateError(error.response?.data?.detail || 'Failed to create URL.');
        } finally {
            setIsCreating(false);
        }
    };

    const handleEditClick = (url) => {
        setUrlToEdit(url);
        setEditUrl(url.original_url);
        setEditAlias(url.short_code);
        setEditError('');
        document.getElementById('edit_modal').showModal();
    };

    const handleEditSubmit = async (e) => {
        e.preventDefault();
        setEditError('');
        setIsEditing(true);

        try {
            const updateData = {};
            if (editUrl !== urlToEdit.original_url) updateData.new_url = editUrl;
            if (editAlias !== urlToEdit.short_code) updateData.new_custom_alias = editAlias;

            if (Object.keys(updateData).length > 0) {
                await apiClient.patch(`/urls/${urlToEdit.short_code}`, updateData);
                fetchUrls();
            }

            document.getElementById('edit_modal').close();
            setUrlToEdit(null);
        } catch (error) {
            setEditError(error.response?.data?.detail || 'Failed to update URL.');
        } finally {
            setIsEditing(false);
        }
    };

    const handleDeleteClick = (url) => {
        setUrlToDelete(url);
        document.getElementById('delete_modal').showModal();
    };

    const confirmDelete = async () => {
        if (!urlToDelete) return;
        try {
            await apiClient.delete(`/urls/${urlToDelete.short_code}`);
            document.getElementById('delete_modal').close();
            setUrlToDelete(null);
            fetchUrls();
        } catch (error) {
            console.error("Failed to delete URL:", error);
        }
    };

    const totalPages = Math.ceil(total / limit) || 1;

    return (
        <div className="max-w-7xl mx-auto p-4 sm:p-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold">Your Links</h1>
                    <p className="text-base-content/70 mt-1">Manage and track your shortened URLs.</p>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={() => document.getElementById('create_modal').showModal()}
                >
                    <Plus className="w-5 h-5" /> Create Link
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center p-12">
                    <span className="loading loading-spinner loading-lg text-primary"></span>
                </div>
            ) : (
                <div className="bg-base-100 rounded-xl shadow-xl overflow-hidden border border-base-300">
                    <div className="overflow-x-auto">
                        <table className="table table-zebra w-full">
                            <thead>
                                <tr className="bg-base-200">
                                    <th>Original URL</th>
                                    <th>Shortened Link</th>
                                    <th>Clicks</th>
                                    <th>Created At</th>
                                    <th className="text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {urls.length === 0 ? (
                                    <tr>
                                        <td colSpan="5" className="text-center py-12 text-base-content/60">
                                            No links found. Create your first one above!
                                        </td>
                                    </tr>
                                ) : (
                                    urls.map((url) => (
                                        <tr key={url.id}>
                                            <td className="max-w-xs truncate" title={url.original_url}>
                                                {url.original_url}
                                            </td>
                                            <td className="font-mono text-primary">
                                                <div className="flex items-center gap-2">
                                                    <a href={`${API_BASE_URL}/${url.short_code}`} target="_blank" rel="noopener noreferrer" className="hover:underline flex items-center gap-1">
                                                        /{url.short_code}
                                                        <ExternalLink className="w-3 h-3" />
                                                    </a>
                                                </div>
                                            </td>
                                            <td>
                                                <div className="badge badge-neutral">{url.clicks_count}</div>
                                            </td>
                                            <td className="text-sm text-base-content/70">
                                                {new Date(url.created_at).toLocaleDateString()}
                                            </td>
                                            <td>
                                                <div className="flex justify-end gap-1">
                                                    <button
                                                        className="btn btn-square btn-sm btn-ghost"
                                                        onClick={() => handleCopy(`${API_BASE_URL}/${url.short_code}`)}
                                                        title="Copy Link"
                                                    >
                                                        <Copy className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        className="btn btn-square btn-sm btn-ghost text-info"
                                                        onClick={() => handleEditClick(url)}
                                                        title="Edit Link"
                                                    >
                                                        <Edit className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        className="btn btn-square btn-sm btn-ghost text-error"
                                                        onClick={() => handleDeleteClick(url)}
                                                        title="Delete Link"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {total > limit && (
                        <div className="flex justify-center p-4 bg-base-200/50 border-t border-base-300">
                            <div className="join">
                                <button className="join-item btn btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>«</button>
                                <button className="join-item btn btn-sm no-animation">Page {page} of {totalPages}</button>
                                <button className="join-item btn btn-sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>»</button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            <dialog id="create_modal" className="modal modal-bottom sm:modal-middle">
                <div className="modal-box">
                    <form method="dialog"><button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button></form>
                    <h3 className="font-bold text-lg mb-4">Create New Short Link</h3>
                    {createError && (
                        <div className="alert alert-error text-sm rounded-lg py-2 mb-4"><AlertCircle className="w-4 h-4" /><span>{createError}</span></div>
                    )}
                    <form onSubmit={handleCreate} className="space-y-4">
                        <div className="form-control">
                            <label className="label"><span className="label-text">Original URL *</span></label>
                            <input type="url" className="input input-bordered w-full" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} required />
                        </div>
                        <div className="form-control">
                            <label className="label"><span className="label-text">Custom Alias (Optional)</span></label>
                            <div className="join w-full">
                                <span className="join-item btn btn-active no-animation cursor-default px-4">/</span>
                                <input
                                    type="text"
                                    className="input input-bordered join-item w-full"
                                    value={customAlias}
                                    onChange={(e) => setCustomAlias(e.target.value)}
                                    pattern="[a-zA-Z0-9-]+"
                                    minLength={5}
                                    title="Letters, numbers, and hyphens (min 5 chars)"
                                />
                            </div>
                        </div>
                        <div className="modal-action mt-6">
                            <form method="dialog"><button className="btn">Cancel</button></form>
                            <button type="submit" className="btn btn-primary" disabled={isCreating}>
                                {isCreating ? <span className="loading loading-spinner"></span> : 'Shorten URL'}
                            </button>
                        </div>
                    </form>
                </div>
                <form method="dialog" className="modal-backdrop"><button>close</button></form>
            </dialog>

            <dialog id="edit_modal" className="modal modal-bottom sm:modal-middle">
                <div className="modal-box">
                    <form method="dialog"><button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" onClick={() => setUrlToEdit(null)}>✕</button></form>
                    <h3 className="font-bold text-lg mb-4">Edit Short Link</h3>

                    {editError && (
                        <div className="alert alert-error text-sm rounded-lg py-2 mb-4">
                            <AlertCircle className="w-4 h-4" /><span>{editError}</span>
                        </div>
                    )}

                    <form onSubmit={handleEditSubmit} className="space-y-4">
                        <div className="form-control">
                            <label className="label"><span className="label-text">Original URL *</span></label>
                            <input type="url" className="input input-bordered w-full" value={editUrl} onChange={(e) => setEditUrl(e.target.value)} required />
                        </div>

                        <div className="form-control">
                            <label className="label">
                                <span className="label-text">Custom Alias</span>
                            </label>
                            <div className="join w-full">
                                <span className="join-item btn btn-active no-animation cursor-default px-4">/</span>
                                <input
                                    type="text"
                                    className="input input-bordered join-item w-full"
                                    value={editAlias}
                                    onChange={(e) => setEditAlias(e.target.value)}
                                    pattern="[a-zA-Z0-9-]+"
                                    minLength={5}
                                    title="Letters, numbers, and hyphens (min 5 chars)"
                                    required
                                />
                            </div>
                        </div>

                        <div className="modal-action mt-6">
                            <form method="dialog">
                                <button className="btn" onClick={() => setUrlToEdit(null)}>Cancel</button>
                            </form>
                            <button type="submit" className="btn btn-primary" disabled={isEditing}>
                                {isEditing ? <span className="loading loading-spinner"></span> : 'Save Changes'}
                            </button>
                        </div>
                    </form>
                </div>
                <form method="dialog" className="modal-backdrop"><button onClick={() => setUrlToEdit(null)}>close</button></form>
            </dialog>

            <dialog id="delete_modal" className="modal modal-bottom sm:modal-middle">
                <div className="modal-box">
                    <h3 className="font-bold text-lg text-error flex items-center gap-2 mb-4">
                        <AlertCircle className="w-5 h-5" /> Confirm Deletion
                    </h3>

                    <p className="mb-4">Are you sure you want to delete this shortened link? This action cannot be undone.</p>

                    <div className="bg-base-200 p-4 rounded-lg border border-base-300 text-sm space-y-3 mb-6">
                        <div>
                            <span className="font-bold text-base-content/70 block mb-1">Short Link:</span>
                            <span className="font-mono text-primary text-base">
                                /{urlToDelete?.short_code}
                            </span>
                        </div>
                        <div>
                            <span className="font-bold text-base-content/70 block mb-1">Points To:</span>
                            <span className="font-mono break-all">
                                {urlToDelete?.original_url}
                            </span>
                        </div>
                    </div>

                    <div className="modal-action">
                        <form method="dialog">
                            <button className="btn" onClick={() => setUrlToDelete(null)}>Cancel</button>
                        </form>
                        <button className="btn btn-error" onClick={confirmDelete}>Yes, Delete</button>
                    </div>
                </div>
                <form method="dialog" className="modal-backdrop">
                    <button onClick={() => setUrlToDelete(null)}>close</button>
                </form>
            </dialog>

        </div>
    );
};

export default Dashboard;