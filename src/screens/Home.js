import React from "react";
import EmptyState from "../components/EmptyState";
import NotificationList from "../components/NotificationList";
import { useNavigate } from "react-router-dom";

export default function Home({ user, notifications, loading, onCreate, onUpdate, onDelete }) {
  const navigate = useNavigate();
  const [error, setError] = React.useState(null);
  const [message, setMessage] = React.useState(null);

  function goNew() {
    navigate('/notifications/new');
  }

  function goEdit(n) {
    navigate(`/notifications/${n.id}/edit`);
  }

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <div className="w-full max-w-3xl bg-white p-6 rounded-xl ">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800">My Notifications</h2>
          {/* make the text white */}
          <button
            onClick={goNew}
            className="text-white px-4 py-2 rounded-lg bg-orange-600 hover:bg-amber-400 transition"
          >
            + New Notification
          </button>
        </div>

        {loading ? (
          <div className="text-center text-gray-500">Loading...</div>
        ) : notifications.length === 0 ? (
          <EmptyState onCreate={goNew} />
        ) : (
          <NotificationList
            items={notifications}
            onEdit={goEdit}
            onDelete={async (id) => {
              setError(null);
              try {
                await onDelete(id);
                setMessage('Notification deleted');
                setTimeout(() => setMessage(null), 2000);
              } catch (err) {
                setError(err.message || 'Unable to delete');
              }
            }}
          />
        )}
        {error && <div className="mt-3 text-sm text-red-600">{error}</div>}
        {message && <div className="mt-3 text-sm text-green-600">{message}</div>}
      </div>
    </div>
  );
}
