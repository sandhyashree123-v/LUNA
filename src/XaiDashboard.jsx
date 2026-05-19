import React, { useEffect, useRef, useState } from "react";
import { API_BASE } from "./apiBase";
import evaluationBenchmark from "../luna_backend_evaluation.json";

const SONOTHERAPY_PROFILES = {
  sad: { label: "432 Hz heart-softening", target: "grief release", weight: 74 },
  anxious: { label: "528 Hz breath field", target: "mental settling", weight: 82 },
  overwhelmed: { label: "Alpha clarity field", target: "pressure reduction", weight: 78 },
  tired: { label: "Theta rest field", target: "deep rest", weight: 70 },
  hopeful: { label: "Gentle uplift field", target: "positive activation", weight: 64 },
  neutral: { label: "Ambient soul field", target: "calm baseline", weight: 52 },
  angry: { label: "Grounding field", target: "heat regulation", weight: 76 },
};

function todayIsoDate() {
  const now = new Date();
  const offsetDate = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return offsetDate.toISOString().slice(0, 10);
}

function clampPercent(value) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, Math.min(100, number)) : 0;
}

function scorePercent(value) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.round(number * 100) : 0;
}

function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "0%";
  return `${Math.round(number)}%`;
}

function formatScore(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "0%";
  return `${Math.round(number * 100)}%`;
}

function metricNumber(...values) {
  for (const value of values) {
    const number = Number(value);
    if (Number.isFinite(number)) return number;
  }
  return 0;
}

function ratioFromPercent(percent, total) {
  const safeTotal = Math.max(0, Number(total) || 0);
  const safePercent = clampPercent(percent);
  return Math.round((safePercent / 100) * safeTotal);
}

function topName(items = []) {
  return items?.[0]?.name || "none";
}

function prettyLabel(value) {
  return String(value || "unknown").replace(/[_-]+/g, " ");
}

function buildUrl(path, params) {
  const query = new URLSearchParams(params);
  return `${API_BASE}${path}?${query.toString()}`;
}

function SignalPill({ label, value, tone = "calm" }) {
  return (
    <span className={`xai-signal-pill xai-signal-${tone}`}>
      <i aria-hidden="true" />
      <span>{label}</span>
      <strong>{value}</strong>
    </span>
  );
}

function MiniPieChart({ segments = [], centerValue, centerLabel }) {
  let cursor = 0;
  const stops = segments.map((segment, index) => {
    const start = cursor;
    const size = Math.max(0, clampPercent(segment.value));
    cursor += size;
    const color = segment.color || ["#9de0c0", "#c8b8e8", "#8aa4b8", "#dcc8be"][index % 4];
    return `${color} ${start}% ${cursor}%`;
  });
  const background = stops.length && cursor > 0
    ? `conic-gradient(${stops.join(", ")}, rgba(255,255,255,0.08) ${cursor}% 100%)`
    : "conic-gradient(rgba(255,255,255,0.1) 0 100%)";

  return (
    <div className="xai-pie-chart">
      <div className="xai-pie-ring" style={{ background }}>
        <div>
          <strong>{centerValue}</strong>
          <span>{centerLabel}</span>
        </div>
      </div>
      <div className="xai-pie-legend">
        {segments.map((segment) => (
          <span key={segment.label}>
            <i style={{ background: segment.color }} aria-hidden="true" />
            {segment.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function HorizontalBar({ label, value, detail, tone = "calm" }) {
  const pct = clampPercent(value);
  return (
    <div className={`xai-horizontal-bar xai-bar-${tone}`}>
      <div>
        <span>{label}</span>
        <strong>{formatPercent(pct)}</strong>
      </div>
      {detail && <small>{detail}</small>}
      <div className="xai-meter-track" aria-hidden="true">
        <i style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function SonotherapyChart({ moods = [], confidence = 0 }) {
  const moodMap = new Map(moods.map((item) => [String(item.name || "").toLowerCase(), item]));
  const visible = Object.entries(SONOTHERAPY_PROFILES).map(([mood, profile]) => ({
    name: mood,
    profile,
    percent: Number(moodMap.get(mood)?.percent || 0),
  }));
  const maxValue = Math.max(1, ...visible.map((item) => item.percent));
  return (
    <div className="xai-sono-chart">
      {visible.map((item) => {
        const usage = clampPercent(item.percent);
        const influence = usage > 0 ? clampPercent((usage * 0.6) + (item.profile.weight * 0.25) + (confidence * 0.15)) : 0;
        return (
          <article className="xai-sono-row" key={item.name}>
            <div className="xai-sono-column-chart" aria-hidden="true">
              <span style={{ height: `${Math.max(4, (usage / maxValue) * 100)}%` }} />
              <i style={{ height: `${Math.max(4, influence)}%` }} />
            </div>
            <span>{item.profile.label}</span>
            <strong>{formatPercent(usage)}</strong>
            <small>{formatPercent(influence)} influence</small>
          </article>
        );
      })}
    </div>
  );
}

function PerformanceGrid({ items = [] }) {
  return (
    <div className="xai-model-chart">
      {items.map((item) => (
        <article className={`xai-model-metric ${item.missing ? "xai-model-metric-missing" : ""}`} key={item.label}>
          <div className="xai-model-bar-rail" aria-hidden="true">
            <i style={{ height: `${clampPercent(item.progress)}%` }} />
          </div>
          <div>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.detail}</small>
          </div>
        </article>
      ))}
    </div>
  );
}

function ImpactMap({ dimensions, wisdomRate, moodConfidence, influenceWeight }) {
  const rows = [
    { label: "Emotion detected", value: moodConfidence, detail: "average classifier confidence" },
    { label: "Response quality", value: scorePercent(dimensions.validation), detail: "validation before advice" },
    { label: "Ancient wisdom", value: wisdomRate, detail: "wisdom retrieved from user context" },
    { label: "Brain influence weight", value: influenceWeight, detail: "support + agency + safety estimate" },
  ];
  return (
    <div className="xai-impact-chart">
      {rows.map((row) => (
        <HorizontalBar key={row.label} label={row.label} value={row.value} detail={row.detail} />
      ))}
    </div>
  );
}

function InsightCard({ label, value, detail }) {
  return (
    <article className="xai-insight-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

function EvaluationRow({ label, value, detail, progress }) {
  const pct = clampPercent(progress);
  return (
    <div className="xai-compare-row">
      <div className="xai-compare-title">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <small>{detail}</small>
      <div className="xai-meter-track"><i style={{ width: `${pct}%` }} /></div>
    </div>
  );
}

export default function XaiDashboard({ userName = "", accounts = [] }) {
  const [day, setDay] = useState(todayIsoDate);
  const [selectedUserName, setSelectedUserName] = useState(userName);
  const [summary, setSummary] = useState(null);
  const [status, setStatus] = useState("Loading audit intelligence...");
  const [auditSignal, setAuditSignal] = useState(0);
  const [revision, setRevision] = useState(null);
  const revisionRef = useRef("");

  useEffect(() => {
    setSelectedUserName(userName);
  }, [userName]);

  const activeUserName = selectedUserName || userName;
  const hasRealUser = activeUserName && activeUserName !== "Choose account";

  useEffect(() => {
    let cancelled = false;
    async function loadSummary() {
      setStatus(hasRealUser ? `Syncing ${activeUserName}'s latest audit record...` : "Choose a Luna account to inspect live chats.");
      let timeout;
      try {
        const controller = new AbortController();
        timeout = window.setTimeout(() => controller.abort(), 8000);
        const params = { day, limit: "200", include_azure: "false" };
        if (hasRealUser) params.user_name = activeUserName;
        const response = await fetch(buildUrl("/xai/dashboard-summary", params), {
          signal: controller.signal,
        });
        if (!response.ok) throw new Error(`Dashboard request failed with ${response.status}`);
        const data = await response.json();
        if (cancelled) return;
        setSummary(data);
        setStatus(data.day !== data.requested_day ? `Showing latest available audit day: ${data.day}` : "");
      } catch {
        if (cancelled) return;
        setSummary(null);
        setStatus("Monitoring data is not available yet.");
      } finally {
        if (timeout) window.clearTimeout(timeout);
      }
    }
    loadSummary();
    const poll = window.setInterval(loadSummary, 6000);
    return () => {
      cancelled = true;
      window.clearInterval(poll);
    };
  }, [day, activeUserName, hasRealUser, auditSignal]);

  useEffect(() => {
    if (typeof window === "undefined" || !("EventSource" in window)) return undefined;
    const params = { day, include_azure: "false" };
    if (hasRealUser) params.user_name = activeUserName;
    const source = new EventSource(buildUrl("/xai/audit-events", params));

    source.onmessage = (event) => {
      try {
        const nextRevision = JSON.parse(event.data);
        setRevision(nextRevision);
        const nextSignature = String(nextRevision.signature || "");
        if (revisionRef.current && nextSignature && nextSignature !== revisionRef.current) {
          setAuditSignal((tick) => tick + 1);
        }
        revisionRef.current = nextSignature;
      } catch {
        setRevision(null);
      }
    };

    source.onerror = () => {
      setStatus("Live audit listener is waiting for the backend.");
    };

    return () => source.close();
  }, [day, activeUserName, hasRealUser]);

  const metrics = summary?.metrics || {};
  const distributions = summary?.distributions || {};
  const dimensions = metrics.average_dimension_scores || {};
  const auditScore = scorePercent(metrics.average_nonjudgment_score);
  const moodConfidence = scorePercent(metrics.average_mood_confidence);
  const totalInteractions = summary?.total_interactions || 0;
  const xaiCoveredCount = ratioFromPercent(metrics.xai_coverage_rate, totalInteractions);
  const privacyPreservedCount = ratioFromPercent(metrics.privacy_preserved_rate, totalInteractions);
  const repairCount = ratioFromPercent(metrics.repair_rate, totalInteractions);
  const validationScore = scorePercent(dimensions.validation);
  const agencyScore = scorePercent(dimensions.agency);
  const safetyScore = scorePercent(dimensions.safety_boundary);
  const supportQuality = Math.round((validationScore * 0.42) + (agencyScore * 0.28) + (safetyScore * 0.18) + (auditScore * 0.12));
  const companionRelevance = Math.round((moodConfidence * 0.24) + (supportQuality * 0.28) + (auditScore * 0.22) + (safetyScore * 0.16) + (clampPercent(metrics.xai_coverage_rate) * 0.1));
  const privacyScore = clampPercent(metrics.privacy_preserved_rate);
  const influenceWeight = Math.round((auditScore * 0.25) + (validationScore * 0.2) + (agencyScore * 0.2) + (safetyScore * 0.2) + (moodConfidence * 0.15));
  const latencyMs = Number(evaluationBenchmark.timings_ms?.detect_mood_avg || 0);
  const promptLatencyMs = Number(evaluationBenchmark.timings_ms?.build_system_prompt_avg || 0);
  const moodAccuracy = Number(evaluationBenchmark.overall_accuracy_percent || 0);
  const latestRevisionLabel = revision?.latest_timestamp
    ? new Date(revision.latest_timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "listening";
  const accountOptions = accounts.length
    ? accounts.map((account) => account.name).filter(Boolean)
    : hasRealUser ? [activeUserName] : [];
  const modelMetrics = [
    { label: "Live emotion confidence", value: formatPercent(moodConfidence), detail: `${totalInteractions} current-user chats`, progress: moodConfidence },
    { label: "Reply audit", value: formatScore(metrics.average_nonjudgment_score), detail: `${totalInteractions} live records`, progress: auditScore },
    { label: "Companion relevance", value: formatPercent(companionRelevance), detail: "mood + support + safety fit", progress: companionRelevance },
    { label: "Support quality", value: formatPercent(supportQuality), detail: "validation + agency + boundary", progress: supportQuality },
    { label: "Mood latency", value: `${latencyMs.toFixed(4)} ms`, detail: "keyword detector avg", progress: 96 },
    { label: "Prompt build", value: `${promptLatencyMs.toFixed(1)} ms`, detail: "system prompt avg", progress: Math.max(4, 100 - promptLatencyMs / 10) },
  ];
  const explainabilitySegments = [
    { label: "Emotion", value: moodConfidence, color: "#9de0c0" },
    { label: "Quality", value: validationScore, color: "#c8b8e8" },
    { label: "Wisdom", value: metrics.wisdom_usage_rate || 0, color: "#dcc8be" },
    { label: "Support", value: influenceWeight, color: "#8aa4b8" },
  ];

  return (
    <div className="xai-dashboard xai-dashboard-lifestats">
      <header className="xai-live-hero">
        <div className="xai-hero-copy">
          <div className="section-kicker">Explainable validation cockpit</div>
          <h2>LUNA System Performance</h2>
        </div>
        <div className="xai-live-controls">
          <SignalPill label="audit stream" value={latestRevisionLabel} tone="live" />
          <select
            className="xai-account-select"
            value={activeUserName || ""}
            onChange={(event) => setSelectedUserName(event.target.value)}
            aria-label="Choose monitoring account"
          >
            {!accountOptions.length && <option value="">Choose account</option>}
            {accountOptions.map((accountName) => (
              <option key={accountName} value={accountName}>{accountName}</option>
            ))}
          </select>
          <button type="button" className="xai-refresh-button" onClick={() => setAuditSignal((tick) => tick + 1)}>
            Refresh
          </button>
          <input className="xai-date-input" type="date" value={day} onChange={(event) => setDay(event.target.value || todayIsoDate())} />
        </div>
      </header>

      {status && <div className="xai-status xai-status-modern">{status}</div>}

      <div className="xai-compact-grid">
        <section className="xai-response-panel xai-glass-panel">
          <div>
            <div className="xai-panel-title">
              <span>Response Explainability</span>
              <small>{totalInteractions} live records</small>
            </div>
            <div className="xai-response-hero">
              <MiniPieChart segments={explainabilitySegments} centerValue={formatPercent(auditScore)} centerLabel="reply audit" />
              <ImpactMap
                dimensions={dimensions}
                wisdomRate={metrics.wisdom_usage_rate || 0}
                moodConfidence={moodConfidence}
                influenceWeight={influenceWeight}
              />
            </div>
          </div>
        </section>

        <section className="xai-sono-panel xai-glass-panel">
          <div className="xai-panel-title">
            <span>Sonotherapeutic Influence</span>
            <small>mood to sound field</small>
          </div>
          <SonotherapyChart moods={distributions.moods || []} confidence={moodConfidence} />
        </section>

        <section className="xai-model-panel xai-glass-panel">
          <div className="xai-panel-title">
            <span>Model Performance</span>
            <small>real metrics only</small>
          </div>
          <PerformanceGrid items={modelMetrics} />
        </section>

        <section className="xai-evidence-panel xai-glass-panel">
          <div>
            <div className="xai-panel-title">
              <span>Evaluation Metrics</span>
              <small>best-fit for companion AI</small>
            </div>
            <EvaluationRow label="Mood accuracy" value={formatPercent(moodAccuracy)} detail={`${evaluationBenchmark.total_cases || 0} labeled backend cases`} progress={moodAccuracy} />
            <EvaluationRow label="Companion relevance" value={formatPercent(companionRelevance)} detail="mood, support, safety, audit fit" progress={companionRelevance} />
            <EvaluationRow label="Empathy quality" value={formatPercent(supportQuality)} detail="validation, agency, boundaries" progress={supportQuality} />
            <EvaluationRow label="Non-judgmental" value={formatPercent(auditScore)} detail={`${totalInteractions} reply audits`} progress={auditScore} />
          </div>
          <div className="xai-insight-grid">
            <InsightCard label="Safety" value={formatPercent(safetyScore)} detail={prettyLabel(topName(distributions.risk_levels))} />
            <InsightCard label="Repair" value={`${repairCount}/${totalInteractions || 0}`} detail="softened replies" />
            <InsightCard label="XAI trace" value={`${xaiCoveredCount}/${totalInteractions || 0}`} detail="coverage" />
            <InsightCard label="Privacy" value={formatPercent(privacyScore)} detail={`${privacyPreservedCount}/${totalInteractions || 0} raw text hidden`} />
          </div>
        </section>
      </div>
    </div>
  );
}
