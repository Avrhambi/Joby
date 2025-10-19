import React, { useState } from "react";
import api from "../utils/api";

export default function AuthForm({ mode = "login", onSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "signup") {
        const res = await api.signup({ email, password, firstName, lastName });
        onSuccess(res.token, res.user);
        // onSuccess("demo-token", { name: "Demo User", email });
      } else {
        const res = await api.login({ email, password });
        onSuccess(res.token, res.user);
        // onSuccess("demo-token", { name: "Demo User", email });

      }
    } catch (err) {
      setError(err.message || "Error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      {mode === "signup" && (
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-sm">First name</label>
            <input value={firstName} onChange={(e) => setFirstName(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
          </div>
          <div>
            <label className="block text-sm">Last name</label>
            <input value={lastName} onChange={(e) => setLastName(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
          </div>
        </div>
      )}
      <div>
        <label className="block text-sm">Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 w-full rounded px-3 py-2 border" />
      </div>
      <div>
        <label className="block text-sm">Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" className="mt-1 w-full rounded px-3 py-2 border" />
      </div>
      {error && <div className="text-sm text-red-600">{error}</div>}
      <div>
        <button disabled={loading} className="bg-orange-600 text-white px-4 py-2 rounded">
          {loading ? "Loading..." : mode === "signup" ? "Sign Up" : "Login"}
        </button>
      </div>
    </form>
  );
}
