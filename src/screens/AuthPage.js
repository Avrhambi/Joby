import React, { useState } from "react";
import AuthForm from "../components/AuthForm";

export default function AuthPage({ onLogin }) {
  const [mode, setMode] = useState("login");
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="p-4">
        <h2 className="text-xl font-semibold mb-4">{mode === "login" ? "Login" : "Sign Up"}</h2>
        <AuthForm mode={mode} onSuccess={onLogin} />
        <div className="mt-4 text-sm text-gray-500">
          {mode === "login" ? (
            <>Don't have an account? <button onClick={() => setMode("signup")} className="text-orange-600">Sign up</button></>
          ) : (
            <>Already have an account? <button onClick={() => setMode("login")} className="text-orange-600">Login</button></>
          )}
        </div>
      </div>
      <div className="p-4 border-l md:border-l-2">
        <h3 className="font-medium">What it does</h3>
        <ul className="list-disc pl-6 mt-2 text-sm text-gray-600">
          <li>Create personalized job notifications</li>
          <li>Send alerts at your chosen frequency</li>
          <li>Email notifications with matching jobs</li>
        </ul>
      </div>
    </div>
  );
}
