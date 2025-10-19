import React from "react";

export default function EmptyState({ onCreate }) {
  return (
    <div className="p-6 border rounded text-center bg-gray-50">
      <div className="mb-4">No notifications yet</div>
      <div className="text-sm text-gray-500 mb-4">Start by creating a new notification with job title, location, and frequency</div>
  <button onClick={onCreate} className="px-4 py-2 rounded bg-orange-600 text-white">Create Notification</button>
    </div>
  );
}
