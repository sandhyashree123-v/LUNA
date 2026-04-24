// src/App.jsx
import React, { Component, useEffect, useState } from "react";
import ChatUI from "./ChatUI";
import DiaryTab from "./DiaryTab";
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

function saveProfile(profile) {
  window.localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
}

function clearSavedProfile() {
  window.localStorage.removeItem(PROFILE_STORAGE_KEY);
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
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState(() => (readSavedProfile() ? "signin" : "signup"));
  const [authName, setAuthName] = useState(() => readSavedProfile()?.name || "");
  const [authPassword, setAuthPassword] = useState("");
  const [authConfirmPassword, setAuthConfirmPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const authButtonLabel = isSignedIn ? "Account" : profile ? "Sign in" : "Sign up";
  const isChatView = activeTab === "chat" && isSignedIn;

  const handleUnlock = (nextProfile) => {
    if (nextProfile) {
      setProfile(nextProfile);
    }
    setIsSignedIn(true);
    setActiveTab("chat");
    setIsAuthModalOpen(false);
    setAuthPassword("");
    setAuthConfirmPassword("");
    setAuthError("");
  };

  const openAuthModal = (preferredMode) => {
    const savedProfile = readSavedProfile();
    setAuthMode(preferredMode || (savedProfile ? "signin" : "signup"));
    setAuthName(savedProfile?.name || "");
    setAuthPassword("");
    setAuthConfirmPassword("");
    setAuthError("");
    setIsAuthModalOpen(true);
  };

  const handleSignOut = () => {
    setIsSignedIn(false);
    setActiveTab("overview");
  };

  const handleReplaceProfile = () => {
    clearSavedProfile();
    setProfile(null);
    setIsSignedIn(false);
    setAuthMode("signup");
    setAuthName("");
    setAuthPassword("");
    setAuthConfirmPassword("");
    setAuthError("");
  };

  const handleAuthSubmit = (event) => {
    event.preventDefault();

    const savedProfile = readSavedProfile();
    const cleanName = authName.trim();
    const cleanPassword = authPassword.trim();
    const cleanConfirm = authConfirmPassword.trim();

    if (authMode === "signup") {
      if (!cleanName) {
        setAuthError("Enter the name Luna should use for you.");
        return;
      }
      if (cleanPassword.length < 4) {
        setAuthError("Use a password with at least 4 characters.");
        return;
      }
      if (cleanPassword !== cleanConfirm) {
        setAuthError("Passwords do not match.");
        return;
      }

      const nextProfile = { name: cleanName, password: cleanPassword };
      saveProfile(nextProfile);
      handleUnlock(nextProfile);
      return;
    }

    if (!savedProfile) {
      setAuthMode("signup");
      setAuthError("No local account found yet. Create one first.");
      return;
    }

    if (cleanPassword !== savedProfile.password) {
      setAuthError("That password doesn't match the saved Luna profile.");
      return;
    }

    handleUnlock(savedProfile);
  };

  useEffect(() => {
    if (!isAuthModalOpen) return undefined;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setIsAuthModalOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isAuthModalOpen]);

  useEffect(() => {
    const { body, documentElement } = document;
    const previousBodyOverflow = body.style.overflow;
    const previousHtmlOverflow = documentElement.style.overflow;

    if (isChatView) {
      body.style.overflow = "hidden";
      documentElement.style.overflow = "hidden";
      body.classList.add("chat-mode-active");
      window.scrollTo(0, 0);
    } else {
      body.classList.remove("chat-mode-active");
    }

    return () => {
      body.style.overflow = previousBodyOverflow;
      documentElement.style.overflow = previousHtmlOverflow;
      body.classList.remove("chat-mode-active");
    };
  }, [isChatView]);

  return (
    <div className={`site-shell ${isChatView ? "site-shell-chat" : ""}`}>
      <div className="site-cosmic-backdrop" />
      <div className="site-stars" />

      {!isChatView && <header className="site-header">
        <button
          type="button"
          className="site-brand"
          onClick={() => setActiveTab(isSignedIn ? "chat" : "overview")}
        >
          <span className="site-brand-mark">
            <span className="site-brand-mark-core" />
            <span className="site-brand-mark-stroke" />
          </span>
          <span>
            <span className="site-brand-name">Luna</span>
            <span className="site-brand-subtitle">Companion</span>
          </span>
        </button>

        <div className="site-header-actions">
          <nav className="site-nav" aria-label="Primary">
            <button
              type="button"
              className={`site-tab-button ${activeTab === "diary" ? "site-tab-button-active" : ""}`}
              onClick={() => setActiveTab("diary")}
            >
              Diary
            </button>
            <button
              type="button"
              className={`site-tab-button ${isAuthModalOpen ? "site-tab-button-active" : ""}`}
              onClick={() => openAuthModal(profile ? "signin" : "signup")}
            >
              {authButtonLabel}
            </button>
          </nav>
          {isSignedIn ? (
            <button type="button" className="site-ghost-button" onClick={handleSignOut}>
              Sign out
            </button>
          ) : null}
        </div>
      </header>}

      <main className={`site-main ${isChatView ? "site-main-chat" : ""}`}>
        {activeTab === "overview" && (
          <section className="minimal-home">
            <div className="minimal-home-brand">
              <div className="minimal-home-logo">
                <span className="minimal-home-logo-core" />
                <span className="minimal-home-logo-orbit" />
              </div>
              <h1 className="minimal-home-title">Luna</h1>
            </div>

            <p className="minimal-home-subtitle">
              A calm space for thoughtful conversation, private journaling, and everyday reflection.
            </p>

            <div className="minimal-presence-strip" aria-label="About Luna">
              <div className="minimal-presence-card">
                <span className="minimal-presence-kicker">Companion</span>
                <strong>Emotion-aware chat</strong>
                <p>Luna listens with care, responds with warmth, and adapts to your emotional tone.</p>
              </div>
              <div className="minimal-presence-card">
                <span className="minimal-presence-kicker">Voice</span>
                <strong>Sonotherapy + speech</strong>
                <p>Ambient soundscapes, natural spoken replies, and a calmer atmosphere in every session.</p>
              </div>
              <div className="minimal-presence-card">
                <span className="minimal-presence-kicker">Memory</span>
                <strong>Private reflection space</strong>
                <p>Pick up your chats, keep personal notes, and stay grounded in one consistent space.</p>
              </div>
            </div>

          </section>
        )}

        {activeTab === "chat" && isSignedIn && (
          <section className="site-content-panel site-content-panel-chat">
            <div className="fade-container">
              <ChatErrorBoundary>
                <ChatUI
                  embedded
                  userName={isSignedIn ? profile?.name || "You" : "You"}
                />
              </ChatErrorBoundary>
            </div>
          </section>
        )}

        {activeTab === "diary" && (
          <section className="site-content-panel">
            <div className="site-section-heading">
              <div>
                <div className="section-kicker">Diary</div>
                <h2>Private Luna diary</h2>
              </div>
              <p>Your notes stay local, and Luna can shape a day-story from today's chats.</p>
            </div>

            <DiaryTab
              userName={isSignedIn ? profile?.name || "You" : "Guest"}
              storageSeed={profile?.name || "guest"}
              isSignedIn={isSignedIn}
              onSignInClick={() => openAuthModal(profile ? "signin" : "signup")}
            />
          </section>
        )}
      </main>

      {isAuthModalOpen && (
        <div className="auth-modal-overlay" onClick={() => setIsAuthModalOpen(false)}>
          <div
            className="auth-modal"
            role="dialog"
            aria-modal="true"
            aria-label="Luna account access"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="auth-modal-header">
              <div>
                <div className="section-kicker">Luna account</div>
                <h2>{isSignedIn ? "Manage your Luna access" : "Sign in or create your Luna profile"}</h2>
              </div>
              <button
                type="button"
                className="auth-close-button"
                onClick={() => setIsAuthModalOpen(false)}
                aria-label="Close dialog"
              >
                ×
              </button>
            </div>

            {isSignedIn ? (
              <div className="auth-signed-in-state">
                <div className="auth-signed-in-card">
                  <div className="auth-signed-in-label">Currently signed in</div>
                  <div className="auth-signed-in-name">{profile?.name || "You"}</div>
                  <p className="auth-signed-in-copy">
                    Your Luna profile is active on this device. You can sign out or replace the saved local profile.
                  </p>
                </div>

                <div className="auth-actions-row">
                  <button type="button" className="site-ghost-button" onClick={handleSignOut}>
                    Sign out
                  </button>
                  <button
                    type="button"
                    className="site-secondary-button"
                    onClick={handleReplaceProfile}
                  >
                    Reset saved profile
                  </button>
                  <button type="button" className="site-primary-button" onClick={() => setIsAuthModalOpen(false)}>
                    Continue
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="auth-mode-switch">
                  <button
                    type="button"
                    className={`auth-mode-button ${authMode === "signin" ? "auth-mode-button-active" : ""}`}
                    onClick={() => {
                      setAuthMode("signin");
                      setAuthError("");
                    }}
                  >
                    Sign in
                  </button>
                  <button
                    type="button"
                    className={`auth-mode-button ${authMode === "signup" ? "auth-mode-button-active" : ""}`}
                    onClick={() => {
                      setAuthMode("signup");
                      setAuthError("");
                    }}
                  >
                    Sign up
                  </button>
                </div>

                <form className="auth-form" onSubmit={handleAuthSubmit}>
                  <div className="auth-form-grid">
                    <label className="auth-field">
                      <span>Name</span>
                      <input
                        type="text"
                        className="auth-input"
                        value={authName}
                        disabled={authMode === "signin" && !!profile}
                        placeholder="How should Luna call you?"
                        onChange={(event) => {
                          setAuthName(event.target.value);
                          if (authError) setAuthError("");
                        }}
                      />
                    </label>

                    <label className="auth-field">
                      <span>Password</span>
                      <input
                        type="password"
                        className="auth-input"
                        value={authPassword}
                        placeholder={authMode === "signin" ? "Enter your password" : "Create a password"}
                        onChange={(event) => {
                          setAuthPassword(event.target.value);
                          if (authError) setAuthError("");
                        }}
                      />
                    </label>

                    {authMode === "signup" && (
                      <label className="auth-field auth-field-full">
                        <span>Confirm password</span>
                        <input
                          type="password"
                          className="auth-input"
                          value={authConfirmPassword}
                          placeholder="Confirm your password"
                          onChange={(event) => {
                            setAuthConfirmPassword(event.target.value);
                            if (authError) setAuthError("");
                          }}
                        />
                      </label>
                    )}
                  </div>

                  <div className="auth-status-line">
                    {authError ||
                      (authMode === "signin"
                        ? profile
                          ? `Welcome back, ${profile.name}. Enter your password to continue.`
                          : "No saved Luna profile yet. Switch to Sign up to create one."
                        : "This Luna profile is stored locally in your browser.")}
                  </div>

                  <div className="auth-actions-row">
                    {profile && authMode === "signin" && (
                      <button
                        type="button"
                        className="site-ghost-button"
                        onClick={handleReplaceProfile}
                      >
                        Start fresh
                      </button>
                    )}
                    <button type="submit" className="site-primary-button">
                      {authMode === "signin" ? "Continue" : "Create account"}
                    </button>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
