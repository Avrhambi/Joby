import React from "react";

const FREQUENCIES = [
  { value: "daily", label: "Daily" },
  { value: "twice_week", label: "Twice a week" },
  { value: "weekly", label: "Weekly" }
];

export default function NotificationList({ items, onEdit, onDelete }) {
  return (
    <div className="space-y-3">
      {items.map((n) => (
        <div key={n.id} className="border rounded p-3 flex items-start justify-between bg-gray-50">
          <div>
            <div className="font-medium">{n.title || "(No Title)"}</div>
            <div className="text-sm text-gray-600 mt-1">
              {`Seniority: ${n.seniority} • Job Scope: ${n.job_scope} • Location: ${n.location} • Country: ${n.country} • Distance: ${n.dist} km`}
            </div>
            <div className="text-xs text-gray-500 mt-1">Frequency: {FREQUENCIES.find(f => f.value === n.frequency)?.label || n.frequency}</div>
            <div className="text-xs text-gray-500 mt-1">Email Enabled: {n.email_enabled ? "Yes" : "No"}</div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => onEdit(n)} className="px-2 py-1 rounded border">Edit</button>
            <button onClick={() => { if (window.confirm('Delete this notification?')) onDelete(n.id); }} className="px-2 py-1 rounded bg-amber-400 text-slate-800">Delete</button>
          </div>
        </div>
      ))}
    </div>
  );
}
