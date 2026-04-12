// src/App.jsx
import React, { Component, useState } from "react";
import LoginScreen from "./LoginScreen";
import ChatUI from "./ChatUI";
import "./App.css";

const PROFILE_STORAGE_KEY = "luna_profile";

function readSavedProfile() {
  try {
    const raw = window.localStorage.getItem(PROFILE_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed?.name || !parsed?.password) return null;
    return { name: String(parsed.name), password: String(parsed.password) };
  } catch {
    return null;
  }
}

class ChatErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div className="app-root" style={{ padding: "2rem" }}>
          <div
            style={{
              maxWidth: "760px",
              margin: "0 auto",
              borderRadius: "24px",
              background: "rgba(10, 14, 32, 0.96)",
              border: "1px solid rgba(255, 170, 170, 0.45)",
              padding: "1.4rem 1.5rem",
              color: "#ffe4e4",
              boxShadow: "0 24px 70px rgba(0,0,0,0.65)",
            }}
          >
            <div style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "0.7rem" }}>
              Luna hit a render glitch
            </div>
            <div style={{ fontSize: "0.95rem", lineHeight: 1.6 }}>
              {this.state.error?.message || "Unknown render error"}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default function App() {
  const [profile, setProfile] = useState(() => readSavedProfile());
  const [unlocked, setUnlocked] = useState(false);

  const handleUnlock = (nextProfile) => {
    if (nextProfile) {
      setProfile(nextProfile);
    }
    setUnlocked(true);
  };

  if (!unlocked) {
    return <LoginScreen onUnlock={handleUnlock} />;
  }

  // fade the whole chat screen in when it first appears
  return (
    <div className="fade-container">
      <ChatErrorBoundary>
        <ChatUI userName={profile?.name || "You"} />
      </ChatErrorBoundary>
    </div>
  );
}
