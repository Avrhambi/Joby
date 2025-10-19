import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate } from 'react-router-dom';
import NotificationPage from './screens/NotificationPage';
import Header from './components/Header';
import AuthPage from './screens/AuthPage';
import Home from './screens/Home';
import UserEdit from './screens/UserEdit';
import api from './utils/api';


// ---------------------- Main App ----------------------
export default function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("jn_token") || null);
  const [notifications, setNotifications] = useState([]);
  const [loadingNotifs, setLoadingNotifs] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      (async () => {
        try {
          const me = await api.getUser(token);
          setUser(me);
          await loadNotifications(token);
        } catch (err) {
          // token invalid or API unreachable
          setToken(null);
          localStorage.removeItem("jn_token");
        }
      })();
    }
  }, [token]);

  async function loadNotifications(tok) {
    setLoadingNotifs(true);
    try {
      const data = await api.getNotifications(tok);
      setNotifications(data);
    } catch {
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
    navigate("/");
  }

 

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6 font-sans">
      <div className="w-full max-w-5xl bg-white rounded-2xl shadow-lg overflow-hidden">
        <Header user={user} onLogout={handleLogout} />
        <div className="p-6">
          <Routes>
            <Route path="/" element={!token ? (
              <AuthPage onLogin={(t, u) => { setToken(t); localStorage.setItem("jn_token", t); setUser(u); navigate('/'); }} />
            ) : (
              <Home
                user={user}
                notifications={notifications}
                loading={loadingNotifs}
                onCreate={async (n) => {
                  // create on backend then prepend
                  const created = token ? await api.createNotification(token, n) : n;
                  console.log(created);
                  setNotifications((prev) => [created, ...prev]);
                }}
                onUpdate={async (updated) => {
                  if (token) {
                    const u = await api.updateNotification(token, updated.id, updated);
                    setNotifications((prev) => prev.map((x) => (x.id === u.id ? u : x)));
                  } else {
                    setNotifications((prev) => prev.map((x) => (x.id === updated.id ? updated : x)));
                  }
                }}
                onDelete={async (id) => {
                  if (token) await api.deleteNotification(token, id);
                  setNotifications((prev) => prev.filter((n) => n.id !== id));
                }}
              />
            )} />

            <Route path="/notifications/new" element={<NotificationPage notifications={notifications} onCreate={async (n) => { const created = token ? await api.createNotification(token, n) : n; setNotifications((prev) => [created, ...prev]); }} onUpdate={async () => {}} onLogout={handleLogout} token={token} />} />
            <Route path="/notifications/:id/edit" element={<NotificationPage notifications={notifications} onCreate={async (n) => { const created = token ? await api.createNotification(token, n) : n; setNotifications((prev) => [created, ...prev]); }} onUpdate={async (n) => { if (token) { const u = await api.updateNotification(token, n.id, n); setNotifications((prev) => prev.map((x) => (x.id === u.id ? u : x))); } else { setNotifications((prev) => prev.map((x) => (x.id === n.id ? n : x))); } }} onLogout={handleLogout} token={token} />} />
            <Route path="/profile" element={<>
              <UserEdit token={token} user={user} onSaved={(u) => setUser(u)} onLogout={handleLogout} />
            </>} />
          </Routes>
        </div>
      </div>
    </div>
  );
}


/* NotificationForm moved to src/screens/NotificationPage.js */
