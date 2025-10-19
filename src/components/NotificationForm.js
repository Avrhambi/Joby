import React, { useState } from 'react';
import { SENIORITY_LEVELS, JOB_SCOPES, FREQUENCIES } from '../utils/constants';

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

export default function NotificationForm({ initial = null, onCancel, onSave, saving = false }) {
  const [title, setTitle] = useState(initial?.title || "");
  const [seniority, setSeniority] = useState(initial?.seniority || "junior");
  const [country, setCountry] = useState(initial?.country || "");
  const [location, setLocation] = useState(initial?.location || "");
  const [dist, setDist] = useState(initial?.dist || 0);
  const [jobScope, setJobScope] = useState(initial?.job_scope || "full time");
  const [frequency, setFrequency] = useState(initial?.frequency || "daily");
  const [emailEnabled, setEmailEnabled] = useState(initial?.email_enabled ?? true);
  const [error, setError] = useState(null);

  function validate() {
    if (!title || !location || !country) return "Please fill in Title, Country, and Location";
    return null;
  }

  function buildNotif() {
    return {
      id: initial?.id || uid(),
      title,
      seniority,
      country,
      location,
      dist,
      job_scope: jobScope,
      frequency,
      email_enabled: emailEnabled
    };
  }

  function submit(e) {
    e.preventDefault();
    const v = validate();
    if (v) { setError(v); return; }
    const notif = buildNotif();
    onSave(notif);
  }

  return (
    <form onSubmit={submit} className="bg-white p-4 rounded border space-y-3 shadow-sm">
      <h4 className="font-medium">{initial ? 'Edit Notification' : 'Create Notification'}</h4>

      <div>
        <label className="text-sm">Title</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-sm">Seniority</label>
          <select value={seniority} onChange={(e) => setSeniority(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border">
            {SENIORITY_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div>
          <label className="text-sm">Job Scope</label>
          <select value={jobScope} onChange={(e) => setJobScope(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border">
            {JOB_SCOPES.map(j => <option key={j} value={j}>{j}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="text-sm">Country</label>
        <input value={country} onChange={(e) => setCountry(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
      </div>

      <div>
        <label className="text-sm">Location (City or District)</label>
        <input value={location} onChange={(e) => setLocation(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
      </div>

      <div>
        <label className="text-sm">Distance (km)</label>
        <input type="number" value={dist} onChange={(e) => setDist(Number(e.target.value))} className="mt-1 w-full rounded px-3 py-2 border" />
      </div>

      <div>
        <label className="text-sm">Frequency</label>
        <select value={frequency} onChange={(e) => setFrequency(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border">
          {FREQUENCIES.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <input id="emailEnabled" type="checkbox" checked={emailEnabled} onChange={(e) => setEmailEnabled(e.target.checked)} />
        <label htmlFor="emailEnabled" className="text-sm">Enable email notifications</label>
      </div>

      {error && <div className="text-sm text-red-600">{error}</div>}

      <div className="flex items-center gap-2">
        <button type="submit" className="px-4 py-2 rounded bg-slate-700 text-white" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
        <button type="button" onClick={onCancel} className="px-3 py-2 rounded border">Cancel</button>
      </div>
    </form>
  );
}
