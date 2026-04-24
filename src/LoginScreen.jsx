import React, { useMemo, useState } from "react";
import "./App.css";
import nebulaVideo from "./assets/nebula.mp4";

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

export default function LoginScreen({ onUnlock, onProfileReset, embedded = false }) {
  const [savedProfile, setSavedProfile] = useState(() => readSavedProfile());
  const [name, setName] = useState(() => readSavedProfile()?.name || "");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLeaving, setIsLeaving] = useState(false);
  const [attemptsLeft, setAttemptsLeft] = useState(3);

  const isSetupMode = !savedProfile;

  const statusLine = useMemo(() => {
    if (error) return error;
    if (isSetupMode) return "Create your local Luna identity to continue.";
    if (attemptsLeft <= 0) return "Access locked for this session.";
    if (password.trim()) return "Credential detected. Validating access.";
    return "Awaiting password verification.";
  }, [attemptsLeft, error, isSetupMode, password]);

  const promptLine = isSetupMode
    ? "New presence detected. Register your name and set the access key."
    : `${savedProfile?.name || "User"}, enter your access key to continue.`;

  const persistAndUnlock = (profile) => {
    window.localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
    setSavedProfile(profile);
    setIsLeaving(true);
    window.setTimeout(() => {
      onUnlock(profile);
    }, 420);
  };

  const resetProfile = () => {
    window.localStorage.removeItem(PROFILE_STORAGE_KEY);
    setSavedProfile(null);
    setName("");
    setPassword("");
    setConfirmPassword("");
    setError("");
    setAttemptsLeft(3);
    onProfileReset?.();
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (isSetupMode) {
      const cleanName = name.trim();
      const cleanPassword = password.trim();

      if (!cleanName) {
        setError("Enter the name Luna should use for you.");
        return;
      }
      if (cleanPassword.length < 4) {
        setError("Use a password with at least 4 characters.");
        return;
      }
      if (cleanPassword !== confirmPassword.trim()) {
        setError("Passwords do not match.");
        return;
      }

      setError("");
      persistAndUnlock({ name: cleanName, password: cleanPassword });
      return;
    }

    if (attemptsLeft <= 0) return;

    const candidate = password.trim();
    if (candidate === savedProfile.password) {
      setError("");
      setIsLeaving(true);
      window.setTimeout(() => {
        onUnlock(savedProfile);
      }, 420);
      return;
    }

    setAttemptsLeft((current) => {
      const next = current - 1;
      if (next <= 0) {
        setError("Access denied. No attempts left in this session.");
        return 0;
      }
      setError(`Access denied. ${next} attempt${next === 1 ? "" : "s"} left.`);
      return next;
    });
  };

  return (
    <div
      className={`login-root ${embedded ? "login-root-embedded" : "login-root-fullscreen"} ${isLeaving ? "login-exit" : ""}`}
    >
      <video autoPlay loop muted playsInline className="nebula-bg">
        <source src={nebulaVideo} type="video/mp4" />
      </video>

      <div className="login-screen-noise" />

      <div className="login-grid">
        <section className="login-character-panel">
          <div className="login-holo-ring login-holo-ring-a" />
          <div className="login-holo-ring login-holo-ring-b" />
          <div className="login-scan-beam" />
          <div className="login-world-dot login-world-dot-a" />
          <div className="login-world-dot login-world-dot-b" />
          <div className="login-world-dot login-world-dot-c" />
          <div className="login-world-dot login-world-dot-d" />

          <div className="login-character-stage">
            <div className="login-sentinel-shadow" />
            <div className="login-sentinel">
              <div className="login-sentinel-core" />
              <div className="login-sentinel-shell login-sentinel-shell-a" />
              <div className="login-sentinel-shell login-sentinel-shell-b" />
              <div className="login-sentinel-eye-band">
                <span className="login-sentinel-eye login-sentinel-eye-left" />
                <span className="login-sentinel-eye login-sentinel-eye-right" />
              </div>
              <div className="login-sentinel-wave login-sentinel-wave-a" />
              <div className="login-sentinel-wave login-sentinel-wave-b" />
              <div className="login-sentinel-pillar login-sentinel-pillar-left" />
              <div className="login-sentinel-pillar login-sentinel-pillar-right" />
              <div className="login-sentinel-base" />
              <div className="login-sentinel-grid" />
            </div>
          </div>

          <div className="login-dialogue-card">
            <div className="login-dialogue-label">LUNA TERMINAL</div>
            <div className="login-dialogue-line">{promptLine}</div>
            <div className="login-dialogue-subline">
              {isSetupMode ? "Local profile creation is enabled." : "Secure gate online. Identity recognized."}
            </div>
          </div>
        </section>

        <section className="login-overlay">
          <div className="login-kicker">Neural Access Console</div>
          <h1 className="login-title">LUNA</h1>
          <div className="login-meta-row">
            <div className="login-status-chip">{statusLine}</div>
            {!isSetupMode ? <div className="login-attempt-pill">{attemptsLeft} attempts left</div> : null}
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            <label className="login-input-label" htmlFor="luna-name">
              {isSetupMode ? "Your Name" : "Registered User"}
            </label>
            <input
              id="luna-name"
              type="text"
              className="login-input"
              placeholder="Enter your name..."
              value={name}
              disabled={!isSetupMode}
              onChange={(event) => {
                setName(event.target.value);
                if (error) setError("");
              }}
            />

            <label className="login-input-label" htmlFor="luna-password">
              {isSetupMode ? "Create Password" : "Password"}
            </label>
            <input
              id="luna-password"
              type="password"
              className="login-input"
              placeholder={isSetupMode ? "Set your password..." : "Enter the password..."}
              value={password}
              disabled={!isSetupMode && attemptsLeft <= 0}
              onChange={(event) => {
                setPassword(event.target.value);
                if (error) setError("");
              }}
            />

            {isSetupMode ? (
              <>
                <label className="login-input-label" htmlFor="luna-password-confirm">
                  Confirm Password
                </label>
                <input
                  id="luna-password-confirm"
                  type="password"
                  className="login-input"
                  placeholder="Confirm the password..."
                  value={confirmPassword}
                  onChange={(event) => {
                    setConfirmPassword(event.target.value);
                    if (error) setError("");
                  }}
                />
              </>
            ) : null}

            <div className={`login-voice-hint ${error ? "login-status-error" : ""}`}>
              {isSetupMode
                ? "This stays local in your browser for now."
                : `Welcome back, ${savedProfile?.name || "User"}. Enter your password to continue.`}
            </div>

            <div className="login-actions">
              <button
                type="submit"
                className="login-button"
                disabled={!isSetupMode && attemptsLeft <= 0}
              >
                {isSetupMode ? "Create Access" : "Authorize"}
              </button>
              {!isSetupMode ? (
                <button
                  type="button"
                  className="login-secondary-button"
                  onClick={resetProfile}
                >
                  Register Again
                </button>
              ) : null}
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
