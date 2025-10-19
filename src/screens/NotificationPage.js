  import React, { useState } from 'react';
  import { useNavigate, useParams } from 'react-router-dom';
  import NotificationForm from '../components/NotificationForm';

  function uid() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  }

  // NotificationForm component moved to src/components/NotificationForm.js

  export default function NotificationPage({ notifications = [], onCreate, onUpdate, onLogout, token }) {
    const navigate = useNavigate();
    const { id } = useParams();
    const initial = id ? notifications.find(n => n.id === id) : null;

    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);

    async function handleSave(n) {
      setError(null);
      setMessage(null);
      setSaving(true);
      try {
        if (initial) {
          await onUpdate(n);
          setMessage('Notification updated');
        } else {
          await onCreate(n);
          setMessage('Notification created');
        }
        // small delay for UX then navigate back
        setTimeout(() => navigate('/'), 500);
      } catch (err) {
        setError(err.message || 'Unable to save notification');
      } finally {
        setSaving(false);
      }
    }

    return (
      <div className="max-w-2xl mx-auto">
        {error && <div className="mb-3 text-sm text-red-600">{error}</div>}
        {message && <div className="mb-3 text-sm text-green-600">{message}</div>}
        <NotificationForm initial={initial} onCancel={() => navigate(-1)} onSave={handleSave} saving={saving} />
      </div>
    );
  }
