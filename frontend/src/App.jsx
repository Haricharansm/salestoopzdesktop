import { useMemo, useState } from "react";
import OrchestrationDashboard from "./components/OrchestrationDashboard";

export default function App() {
  const [tab, setTab] = useState("orchestrator");

  const tabs = useMemo(
    () => [
      { id: "orchestrator", label: "Autonomous Orchestrator" },
      { id: "settings", label: "Settings (M365)" },
    ],
    []
  );

  return (
    <div className="container">
      <div className="topbar">
        <div>
          <h1>Salestroopz Desktop</h1>
          <p>Local-first autonomous SDR agent (Option C).</p>
        </div>
        <span className="badge warn">Local-first • MVP</span>
      </div>

      <div className="tabs">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={`tab ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "orchestrator" ? (
        <OrchestrationDashboard />
      ) : (
        <div className="card">
          <h2>Microsoft 365 (Outlook) Integration</h2>
          <p>
            Next: add Microsoft Identity login + Graph scopes. For now, keep your
            SendGrid path as fallback.
          </p>
          <div className="row" style={{ marginTop: 12 }}>
            <div className="col">
              <label>Tenant Type</label>
              <select defaultValue="common">
                <option value="common">common (multi-tenant)</option>
                <option value="organizations">organizations</option>
              </select>
            </div>
            <div className="col">
              <label>Sending Mode</label>
              <select defaultValue="m365">
                <option value="m365">Microsoft 365 Mailbox</option>
                <option value="sendgrid">SendGrid (fallback)</option>
              </select>
            </div>
          </div>

          <div className="row" style={{ marginTop: 12 }}>
            <button className="btn primary">Connect Microsoft 365</button>
            <button className="btn">Test Connection</button>
          </div>

          <p style={{ marginTop: 10 }}>
            Wire this to Electron later using an auth window (MSAL) and store tokens
            securely (DPAPI / Windows Credential Manager).
          </p>
        </div>
      )}
    </div>
  );
}
