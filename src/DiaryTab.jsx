import React, { useEffect, useMemo, useState } from "react";

const API_BASE = (() => {
  const configuredBase = import.meta.env.VITE_API_BASE_URL?.trim().replace(/\/+$/, "");
  if (configuredBase) return configuredBase;

  if (typeof window !== "undefined") {
    const { hostname, origin } = window.location;
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      return "http://127.0.0.1:8000";
    }
    return origin.replace(/\/+$/, "");
  }

  return "http://127.0.0.1:8000";
})();

function createDiaryStorageKey(seed) {
  const normalized = String(seed || "guest")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-");

  return `luna_diary_entries:${normalized || "guest"}`;
}

function formatEntryDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Just now";

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function createAutoEntryId(value) {
  return `luna-auto-story:${value || "today"}`;
}

export default function DiaryTab({
  userName = "Guest",
  storageSeed = "guest",
  isSignedIn = false,
  onSignInClick,
}) {
  const storageKey = useMemo(() => createDiaryStorageKey(storageSeed), [storageSeed]);
  const [entries, setEntries] = useState([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [status, setStatus] = useState("");
  const [isGeneratingStory, setIsGeneratingStory] = useState(false);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(storageKey);
      if (!saved) {
        setEntries([]);
        return;
      }

      const parsed = JSON.parse(saved);
      setEntries(Array.isArray(parsed) ? parsed : []);
    } catch {
      setEntries([]);
    }
  }, [storageKey]);

  useEffect(() => {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(entries));
    } catch {
      setStatus("Luna couldn't save this diary update locally.");
    }
  }, [entries, storageKey]);

  useEffect(() => {
    if (!isSignedIn) return undefined;

    let cancelled = false;
    const loadLunaStory = async () => {
      setIsGeneratingStory(true);

      try {
        const response = await fetch(
          `${API_BASE}/diary/story?user_name=${encodeURIComponent(userName)}&language=en-IN`
        );
        if (!response.ok) {
          throw new Error(`Diary story request failed with ${response.status}`);
        }

        const data = await response.json();
        if (cancelled || !data?.story?.trim()) return;

        const autoEntry = {
          id: createAutoEntryId(data.date),
          title: data.title?.trim() || "Luna's note for today",
          body: data.story.trim(),
          createdAt: data.generated_at || new Date().toISOString(),
          kind: "luna-auto",
          sourceCount: Number(data.entry_count || 0),
        };

        setEntries((current) => {
          const withoutSameAuto = current.filter((entry) => entry.id !== autoEntry.id);
          return [autoEntry, ...withoutSameAuto];
        });
      } catch {
        if (!cancelled) {
          setStatus((current) => current || "Luna couldn't shape today's diary story right now.");
        }
      } finally {
        if (!cancelled) {
          setIsGeneratingStory(false);
        }
      }
    };

    loadLunaStory();
    return () => {
      cancelled = true;
    };
  }, [isSignedIn, userName, storageKey]);

  const handleSave = () => {
    const cleanBody = body.trim();
    const cleanTitle = title.trim();

    if (!cleanBody) {
      setStatus("Write a few lines before saving your entry.");
      return;
    }

    const nextEntry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      title: cleanTitle || "Untitled entry",
      body: cleanBody,
      createdAt: new Date().toISOString(),
    };

    setEntries((current) => [nextEntry, ...current]);
    setTitle("");
    setBody("");
    setStatus("Diary entry saved locally.");
  };

  const handleDelete = (entryId) => {
    setEntries((current) => current.filter((entry) => entry.id !== entryId));
    setStatus("Diary entry removed.");
  };

  return (
    <div className="diary-shell">
      <div className="diary-hero-card">
        <div>
          <div className="section-kicker">Reflect</div>
          <h3 className="diary-hero-title">A calm space for {userName}&apos;s thoughts.</h3>
          <p className="diary-hero-text">
            Save private reflections, small wins, and emotional check-ins. Luna also turns today's conversations into a soft diary story for you.
          </p>
        </div>

        <div className="diary-stats">
          <div className="diary-stat-card">
            <span className="diary-stat-label">Entries</span>
            <strong>{entries.length}</strong>
          </div>
          <div className="diary-stat-card">
            <span className="diary-stat-label">Mode</span>
            <strong>{isSignedIn ? "Personal" : "Guest"}</strong>
          </div>
        </div>
      </div>

      <div className="diary-grid">
        <div className="diary-composer-card">
          <label className="diary-label" htmlFor="luna-diary-title">
            Title
          </label>
          <input
            id="luna-diary-title"
            className="diary-input"
            type="text"
            value={title}
            placeholder="Today felt like..."
            onChange={(event) => {
              setTitle(event.target.value);
              if (status) setStatus("");
            }}
          />

          <label className="diary-label" htmlFor="luna-diary-body">
            Entry
          </label>
          <textarea
            id="luna-diary-body"
            className="diary-textarea"
            value={body}
            placeholder="Write whatever is on your mind. It can be messy, honest, short, or long."
            onChange={(event) => {
              setBody(event.target.value);
              if (status) setStatus("");
            }}
          />

          <div className="diary-actions">
            <button type="button" className="site-primary-button" onClick={handleSave}>
              Save entry
            </button>
            <button
              type="button"
              className="site-secondary-button"
              onClick={() => {
                setTitle("");
                setBody("");
                setStatus("");
              }}
            >
              Clear
            </button>
          </div>

          <div className="diary-status">{status || "Tip: use the diary for emotions, gratitude, or quick daily notes."}</div>
          {isSignedIn && (
            <div className="diary-auto-hint">
              {isGeneratingStory ? "Luna is shaping today's diary story..." : "Today's Luna story refreshes automatically from your chats."}
            </div>
          )}

          {!isSignedIn && typeof onSignInClick === "function" && (
            <button type="button" className="diary-inline-link" onClick={onSignInClick}>
              Sign in or sign up if you want Luna chat and diary to feel more personal.
            </button>
          )}
        </div>

        <div className="diary-history-card">
          <div className="diary-history-header">
            <h3>Saved entries</h3>
            <span>{entries.length ? `${entries.length} total` : "No entries yet"}</span>
          </div>

          {entries.length === 0 ? (
            <div className="diary-empty-state">
              Your diary is empty right now. Write your first note and it will show up here.
            </div>
          ) : (
            <div className="diary-entry-list">
              {entries.map((entry) => (
                <article key={entry.id} className="diary-entry-card">
                  <div className="diary-entry-top">
                    <div>
                      {entry.kind === "luna-auto" && <div className="diary-entry-badge">Luna's story</div>}
                      <h4>{entry.title}</h4>
                      <div className="diary-entry-date">{formatEntryDate(entry.createdAt)}</div>
                    </div>
                    {entry.kind !== "luna-auto" ? (
                      <button
                        type="button"
                        className="diary-delete-button"
                        onClick={() => handleDelete(entry.id)}
                      >
                        Delete
                      </button>
                    ) : (
                      <div className="diary-entry-meta">{entry.sourceCount ? `${entry.sourceCount} chat moments` : "Auto-written from chat"}</div>
                    )}
                  </div>
                  <p>{entry.body}</p>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
