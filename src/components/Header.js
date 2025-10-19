import React from "react";
import { useNavigate } from "react-router-dom";

export default function Header({ user, onLogout }) {
  const navigate = useNavigate();

  
  // Determine greeting based on current hour
  const hour = new Date().getHours();
  let greeting = "Hello";
  if (hour < 12) greeting = "Good morning";
  else if (hour < 18) greeting = "Good afternoon";
  else greeting = "Good evening";

  function getFirstName(u) {
    if (!u) return '';
    if (u.firstName) return capitalize(u.firstName);
    if (u.name) {
      const parts = String(u.name).trim().split(/\s+/);
      if (parts.length) return capitalize(parts[0]);
    }
    if (u.email) return capitalize(String(u.email).split('@')[0]);
    return '';
  }

  function capitalize(s) {
    if (!s) return '';
    const str = String(s).trim();
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  return (
  <header className="flex items-center justify-between bg-orange-600 text-white px-6 py-3 relative">
      {/* Left section */}
      <div
        className="flex items-center gap-2 cursor-pointer"
        onClick={() => navigate("/")}
      >
        <div className="text-2xl font-bold">Joby</div>
        <div className="text-sm opacity-80 hidden sm:block">
          Automatic job alerts
        </div>
      </div>

      {/* Center section */}
      {user && (
        <div className="absolute left-1/2 transform -translate-x-1/2 text-medium  font-medium">
          {greeting}, {getFirstName(user)}
        </div>
      )}

      {/* Right section */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate("/")}
          className="px-3 py-1 rounded bg-white/20 hover:bg-white/30 transition"
        >
          Home
        </button>
        {user && (
          <button
            onClick={() => navigate('/profile')}
            className="px-3 py-1 rounded bg-white/20 hover:bg-white/30 transition"
          >
            Profile
          </button>
        )}
        {user && (
          <button
            onClick={onLogout}
            className="bg-white text-orange-600 px-3 py-1 rounded hover:bg-gray-100 transition"
          >
            Logout
          </button>
        )}
      </div>
    </header>
  );
}
