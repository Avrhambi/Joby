import React, { useState, useEffect } from "react";

// Single-file React frontend for the Job Notifier app
// - Tailwind CSS utility classes are used for styling (no imports here)
// - State persists to localStorage so you can try flows without a backend
// - Replace `api.*` functions with real HTTP calls to your backend (JWT auth)

// ---------------------- Mock API helpers (replace with real fetch calls) ----------------------
const api = {
  signup: async ({ email, password, name }) => {
    // In production: POST /api/auth/signup -> returns { token }
    const users = JSON.parse(localStorage.getItem("jn_users") || "[]");
    if (users.find((u) => u.email === email)) throw new Error("User exists");
    const user = { id: Date.now().toString(), email, passwordHash: password, name };
    users.push(user);
    localStorage.setItem("jn_users", JSON.stringify(users));
    // return fake token
    return { token: `fake-jwt-${user.id}`, user: { id: user.id, email, name } };
  },
  login: async ({ email, password }) => {
    const users = JSON.parse(localStorage.getItem("jn_users") || "[]");
    const user = users.find((u) => u.email === email && u.passwordHash === password);
    if (!user) throw new Error("Invalid credentials");
    return { token: `fake-jwt-${user.id}`, user: { id: user.id, email: user.email, name: user.name } };
  },
  getNotifications: async (token) => {
    // token -> user id
    const uid = token?.split("-").pop();
    const key = `jn_notifs_${uid}`;
    return JSON.parse(localStorage.getItem(key) || "[]");
  },
  saveNotifications: async (token, notifs) => {
    const uid = token?.split("-").pop();
    localStorage.setItem(`jn_notifs_${uid}`, JSON.stringify(notifs));
    return notifs;
  }
};

// ---------------------- Utility helpers ----------------------
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

// Frequencies (Hebrew labels included)
const FREQUENCIES = [
  { value: "twice_day", label: "פעמיים ביום" },
  { value: "once_day", label: "פעם ביום" },
  { value: "every_two_days", label: "פעם ביומיים" },
  { value: "once_week", label: "פעם בשבוע" }
];

const JOB_LEVELS = ["junior", "mid", "senior", "chief"];
const EMPLOYMENT_TYPES = ["full_time", "part_time", "internship"];

// ---------------------- Main App ----------------------
export default function App() {
  const [page, setPage] = useState("home"); // 'auth' or 'home'
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("jn_token") || null);
  const [notifications, setNotifications] = useState([]);
  const [loadingNotifs, setLoadingNotifs] = useState(false);

  useEffect(() => {
    // If token exists, fetch user info and notifications (mock)
    if (token) {
      // decode fake token
      const uidVal = token.split("-").pop();
      const users = JSON.parse(localStorage.getItem("jn_users") || "[]");
      const u = users.find((x) => x.id === uidVal);
      if (u) {
        setUser({ id: u.id, email: u.email, name: u.name });
        loadNotifications(token);
        setPage("home");
      } else {
        setToken(null);
        localStorage.removeItem("jn_token");
      }
    }
  }, [token]);

  async function loadNotifications(tok) {
    setLoadingNotifs(true);
    try {
      const data = await api.getNotifications(tok);
      setNotifications(data);
    } catch (err) {
      console.error(err);
      setNotifications([]);
    } finally {
      setLoadingNotifs(false);
    }
  }

  async function handleLogout() {
    setToken(null);
    localStorage.removeItem("jn_token");
    setUser(null);
    setNotifications([]);
    setPage("auth");
  }

  // persist notifications to storage (mock save)
  async function persistNotifs(notifs) {
    setNotifications(notifs);
    if (!token) return; // no-op
    await api.saveNotifications(token, notifs);
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-md overflow-hidden">
        <Header user={user} onLogout={handleLogout} onNavigate={setPage} currentPage={page} />
        <div className="p-6">
          {!token ? (
            <AuthPage onLogin={(t, u) => { setToken(t); localStorage.setItem("jn_token", t); setUser(u); }} />
          ) : (
            <Home
              user={user}
              notifications={notifications}
              loading={loadingNotifs}
              onCreate={async (n) => {
                const newList = [n, ...notifications];
                await persistNotifs(newList);
              }}
              onUpdate={async (updated) => {
                const newList = notifications.map((n) => (n.id === updated.id ? updated : n));
                await persistNotifs(newList);
              }}
              onDelete={async (id) => {
                const newList = notifications.filter((n) => n.id !== id);
                await persistNotifs(newList);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------- Header ----------------------
function Header({ user, onLogout, onNavigate, currentPage }) {
  return (
    <div className="flex items-center justify-between bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4">
      <div className="flex items-center gap-3">
        <div className="text-2xl font-bold">JobNotifier</div>
        <div className="text-sm opacity-80">התרעות משרות אוטומטיות</div>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={() => onNavigate("home")}
          className={`px-3 py-1 rounded ${currentPage === "home" ? "bg-white/20" : "bg-white/10"}`}
        >
          הבית
        </button>
        {user ? (
          <div className="flex items-center gap-2">
            <div className="text-sm">{user.name || user.email}</div>
            <button onClick={onLogout} className="bg-white text-indigo-600 px-3 py-1 rounded">התנתק</button>
          </div>
        ) : null}
      </div>
    </div>
  );
}

// ---------------------- Auth Page ----------------------
function AuthPage({ onLogin }) {
  const [mode, setMode] = useState("login");
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="p-4">
        <h2 className="text-xl font-semibold mb-4">{mode === "login" ? "התחברות" : "הרשמה"}</h2>
        <AuthForm mode={mode} onSuccess={(token, user) => onLogin(token, user)} />
        <div className="mt-4 text-sm text-gray-500">
          {mode === "login" ? (
            <>
              אין לך חשבון? <button onClick={() => setMode("signup")} className="text-indigo-600">צור חשבון</button>
            </>
          ) : (
            <>
              כבר יש חשבון? <button onClick={() => setMode("login")} className="text-indigo-600">התחבר</button>
            </>
          )}
        </div>
      </div>

      <div className="p-4 border-l md:border-l-0 md:border-l-2">
        <h3 className="font-medium">מה זה עושה?</h3>
        <ul className="list-disc pr-6 mt-2 text-sm text-gray-600">
          <li>יצירת התראות חיפוש עבודה מותאמות אישית</li>
          <li>שליחה בתדירויות שתבחרו (ממשק לדוגמה)</li>
          <li>שליחת דוא"ל אוטומטי עם משרות מתאימות</li>
        </ul>
      </div>
    </div>
  );
}

function AuthForm({ mode = "login", onSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "signup") {
        const res = await api.signup({ email, password, name });
        onSuccess(res.token, res.user);
      } else {
        const res = await api.login({ email, password });
        onSuccess(res.token, res.user);
      }
    } catch (err) {
      setError(err.message || "שגיאה");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      {mode === "signup" && (
        <div>
          <label className="block text-sm">שם מלא</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
        </div>
      )}
      <div>
        <label className="block text-sm">מייל</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
      </div>
      <div>
        <label className="block text-sm">סיסמה</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" className="mt-1 w-full rounded px-3 py-2 border" />
      </div>
      {error && <div className="text-sm text-red-600">{error}</div>}
      <div>
        <button disabled={loading} className="bg-indigo-600 text-white px-4 py-2 rounded">
          {loading ? "טוען..." : mode === "signup" ? "הרשמה" : "התחבר"}
        </button>
      </div>
    </form>
  );
}

// ---------------------- Home Page ----------------------
function Home({ user, notifications, loading, onCreate, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    setShowForm(false);
    setEditing(null);
  }, [notifications.length]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">התראות שלי</h2>
          <div className="flex items-center gap-2">
            <button onClick={() => { setEditing(null); setShowForm(true); }} className="px-3 py-1 rounded bg-green-600 text-white">צור התראה חדשה</button>
            <button onClick={() => { setShowForm((s) => !s); }} className="px-3 py-1 rounded border">הצג/הסתר טופס</button>
          </div>
        </div>

        {loading ? (
          <div>טוען...</div>
        ) : notifications.length === 0 ? (
          <EmptyState onCreate={() => { setEditing(null); setShowForm(true); }} />
        ) : (
          <NotificationList items={notifications} onEdit={(n) => { setEditing(n); setShowForm(true); }} onDelete={onDelete} />
        )}
      </div>

      <div>
        <div className="bg-white p-4 rounded shadow-sm">
          <h3 className="font-semibold mb-2">הגדרות התראות</h3>
          <p className="text-sm text-gray-600">ניהול התראות, שליחת דוא"ל ותדירות. באפשרותך להוסיף, לערוך או למחוק התראות מהצד הזה.</p>
          <div className="mt-4">
            <div className="text-sm mb-2">סוג משרה לדוגמה</div>
            <div className="flex gap-2">
              <Badge>junior</Badge>
              <Badge>senior</Badge>
              <Badge>part time</Badge>
            </div>
          </div>
        </div>

        {showForm && (
          <div className="mt-4">
            <NotificationForm initial={editing} onCancel={() => setShowForm(false)} onSave={async (n) => { if (editing) await onUpdate(n); else await onCreate(n); setShowForm(false); }} />
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyState({ onCreate }) {
  return (
    <div className="p-6 border rounded text-center">
      <div className="mb-4">אין לך התראות כרגע</div>
      <div className="text-sm text-gray-600 mb-4">התחל על ידי יצירת התראה חדשה עם מילות חיפוש, מיקום ותדירות</div>
      <button onClick={onCreate} className="px-4 py-2 rounded bg-indigo-600 text-white">צור התראה</button>
    </div>
  );
}

function Badge({ children }) {
  return <div className="text-xs px-2 py-1 bg-gray-100 rounded">{children}</div>;
}

// ---------------------- Notification List ----------------------
function NotificationList({ items, onEdit, onDelete }) {
  return (
    <div className="space-y-3">
      {items.map((n) => (
        <div key={n.id} className="border rounded p-3 flex items-start justify-between">
          <div>
            <div className="font-medium">{n.title || n.keywords || "(לא הוגדר שם)"}</div>
            <div className="text-sm text-gray-600 mt-1">{renderSummary(n)}</div>
            <div className="text-xs text-gray-500 mt-2">תדירות: {FREQUENCIES.find(f => f.value === n.frequency)?.label || n.frequency}</div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => onEdit(n)} className="px-2 py-1 rounded border">עריכה</button>
            <button onClick={() => { if (window.confirm('Delete this notification?')) onDelete(n.id); }} className="px-2 py-1 rounded bg-red-600 text-white">מחק</button>
          </div>
        </div>
      ))}
    </div>
  );
}

function renderSummary(n) {
  const parts = [];
  if (n.keywords) parts.push(`מילים: ${n.keywords}`);
  if (n.level) parts.push(`דרגה: ${n.level}`);
  if (n.location) parts.push(`מיקום: ${n.location}`);
  if (n.employmentType) parts.push(`היקף: ${n.employmentType}`);
  if (n.includeWeekends) parts.push(`כולל סופ"ש`);
  return parts.join(' • ');
}

// ---------------------- Notification Form ----------------------
function NotificationForm({ initial = null, onCancel, onSave }) {
  const [title, setTitle] = useState(initial?.title || "");
  const [keywords, setKeywords] = useState(initial?.keywords || "");
  const [level, setLevel] = useState(initial?.level || "junior");
  const [location, setLocation] = useState(initial?.location || "");
  const [employmentType, setEmploymentType] = useState(initial?.employmentType || "full_time");
  const [frequency, setFrequency] = useState(initial?.frequency || "once_day");
  const [includeWeekends, setIncludeWeekends] = useState(initial?.includeWeekends || false);
  const [emailEnabled, setEmailEnabled] = useState(initial?.emailEnabled || false);
  const [error, setError] = useState(null);

  // function singleJobMode() {
  //   // The user asked to allow entering only one job optionally.
  //   // We'll limit keywords to the first segment before a comma when the single-job toggle is used.
  //   // For simplicity, we provide a checkbox that enforces single job.
  // }

  function buildNotif() {
    return {
      id: initial?.id || uid(),
      title: title || keywords.split(',')[0].trim(),
      keywords: keywords,
      level,
      location,
      employmentType,
      frequency,
      includeWeekends,
      emailEnabled,
      createdAt: initial?.createdAt || new Date().toISOString()
    };
  }

  function validate() {
    if (!keywords && !title) return "יש להזין שם משרה או מילת חיפוש";
    return null;
  }

  function submit(e) {
    e.preventDefault();
    const v = validate();
    if (v) {
      setError(v);
      return;
    }
    const notif = buildNotif();
    onSave(notif);
  }

  return (
    <form onSubmit={submit} className="bg-white p-4 rounded border space-y-3">
      <h4 className="font-medium">{initial ? 'עריכת התראה' : 'יצירת התראה'}</h4>
      <div>
        <label className="text-sm">שם/כותרת (אופציונלי)</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
      </div>

      <div>
        <label className="text-sm">שם משרה / מילות חיפוש (מופרדות בפסיקים) - אפשר להכניס גם משרה אחת בלבד</label>
        <input value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder="לדוגמה: מהנדס תוכנה, backend" className="mt-1 w-full rounded px-3 py-2 border" />
        <div className="text-xs text-gray-500 mt-1">כדי להכניס רק משרה אחת: כתבו רק שם אחד (ללא פסיקים) — המערכת תשתמש במילה הראשונה גם כשם ברירת מחדל.</div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-sm">דרגת משרה</label>
          <select value={level} onChange={(e) => setLevel(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border">
            {JOB_LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div>
          <label className="text-sm">היקף משרה</label>
          <select value={employmentType} onChange={(e) => setEmploymentType(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border">
            {EMPLOYMENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="text-sm">מיקום (עיר / איזור)</label>
        <input value={location} onChange={(e) => setLocation(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
      </div>

      <div className="grid grid-cols-2 gap-2 items-center">
        <div>
          <label className="text-sm">תדירות משלוח</label>
          <select value={frequency} onChange={(e) => setFrequency(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border">
            {FREQUENCIES.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <input id="weekends" type="checkbox" checked={includeWeekends} onChange={(e) => setIncludeWeekends(e.target.checked)} />
          <label htmlFor="weekends" className="text-sm">כולל סופי שבוע</label>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input id="emailEnabled" type="checkbox" checked={emailEnabled} onChange={(e) => setEmailEnabled(e.target.checked)} />
        <label htmlFor="emailEnabled" className="text-sm">שליחת דוא"ל עם המשרות</label>
      </div>

      {error && <div className="text-sm text-red-600">{error}</div>}

      <div className="flex items-center gap-2">
        <button type="submit" className="px-4 py-2 rounded bg-indigo-600 text-white">שמור</button>
        <button type="button" onClick={onCancel} className="px-3 py-2 rounded border">ביטול</button>
      </div>
    </form>
  );
}

// ---------------------------------------------------------------------------------
// Notes (in-code):
// - Replace the `api` object with real API calls for signup/login and notifications.
// - Use secure password hashing + HTTPS on the backend.
// - Replace localStorage fake token with real JWT handling and token refresh.
// - Add client-side validation and friendlier UX (date/time pickers for schedule, etc.).
// - To integrate with job scraping APIs, implement server endpoints that run searches and send emails on schedule.
// ---------------------------------------------------------------------------------
