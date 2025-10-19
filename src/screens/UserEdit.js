import React, { useEffect, useState } from 'react';
import api from '../utils/api';

export default function UserEdit({ token, user, onSaved, onLogout }) {
  const [form, setForm] = useState({ name: '', email: '', currentPassword: '', newPassword: '', confirm: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (user) setForm((f) => ({ ...f, name: user.name || '', email: user.email || '' }));
    else if (token) {
      (async () => {
        try {
          const me = await api.getUser(token);
          setForm((f) => ({ ...f, name: me.name || '', email: me.email || '' }));
        } catch (e) {
          setError(e.message);
        }
      })();
    }
  }, [user, token]);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      // update basic profile first
      const updated = await api.updateUser(token, { name: form.name, email: form.email });

      // if user provided a new password, validate and change it
      if (form.newPassword) {
        if (!form.currentPassword) throw new Error('Current password is required to change password');
        if (form.newPassword !== form.confirm) throw new Error('New password and confirm do not match');
        await api.changePassword(token, { currentPassword: form.currentPassword, newPassword: form.newPassword });
      }

      setMessage('Profile updated successfully');
      if (onSaved) onSaved(updated);
      // clear passwords
      setForm((f) => ({ ...f, currentPassword: '', newPassword: '', confirm: '' }));
    } catch (e) {
      setError(e.message || 'Error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <h3 className="text-lg font-semibold mb-4">Edit Profile</h3>
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="text-sm">Name</label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="mt-1 w-full rounded px-3 py-2 border" />
        </div>
        <div>
          <label className="text-sm">Email</label>
          <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1 w-full rounded px-3 py-2 border" />
        </div>


        <div className="">
          <div className="mt-2">
            <label className="text-sm">Current password</label>
            <input type="password" value={form.currentPassword} onChange={(e) => setForm({ ...form, currentPassword: e.target.value })} className="mt-1 w-full rounded px-3 py-2 border" />
          </div>
          <div>
            <label className="text-sm">New password</label>
            <input type="password" value={form.newPassword} onChange={(e) => setForm({ ...form, newPassword: e.target.value })} className="mt-1 w-full rounded px-3 py-2 border" />
          </div>
          <div>
            <label className="text-sm">Confirm new password</label>
            <input type="password" value={form.confirm} onChange={(e) => setForm({ ...form, confirm: e.target.value })} className="mt-1 w-full rounded px-3 py-2 border" />
          </div>
        </div>

        {error && <div className="text-sm text-red-600">{error}</div>}
        {message && <div className="text-sm text-green-600">{message}</div>}

        <div className="flex items-center gap-2">
          <button disabled={loading} className="px-4 py-2 rounded bg-slate-700 text-white">Save</button>
          <button type="button" onClick={onLogout} className="px-3 py-2 rounded border">Logout</button>
        </div>
      </form>
    </div>
  );
}
