import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_AGENT_URL || "http://127.0.0.1:8000";

export default function M365Connect() {
  const [status, setStatus] = useState({ loading: true });
  const [flow, setFlow] = useState(null);
  const [error, setError] = useState("");

  const refreshStatus = async () => {
    try {
      setError("");
      const res = await fetch(`${API_BASE}/m365/status`);
      const data = await res.json();
      setStatus({ loading: false, ...data });
    } catch (e) {
      setStatus({ loading: false, connected: false });
      setError("Agent not reachable. Is FastAPI running on 127.0.0.1:8000?");
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  const startConnect = async () => {
    try {
      setError("");
      const res = await fetch(`${API_BASE}/m365/device/start`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Failed to start device flow");
      setFlow(data);
    } catch (e) {
      setError(e.message);
    }
  };

  const completeConnect = async () => {
    try {
      setError("");
      const res = await fetch(`${API_BASE}/m365/device/complete`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Failed to complete device flow");
      setFlow(null);
      await refreshStatus();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="card">
      <h2>Microsoft 365 Integration</h2>
      <p>Connect Outlook mailbox to send campaigns</p>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {status.loading ? (
        <p>Checking connection...</p>
      ) : status.connected ? (
        <div>
          <p style={{ color: "green" }}>
            Connected: {status.user?.displayName} ({status.user?.mail})
          </p>
          <button onClick={refreshStatus}>Refresh</button>
        </div>
      ) : (
        <div>
          {!flow ? (
            <button onClick={startConnect}>Connect Microsoft 365</button>
          ) : (
            <div style={{ marginTop: 12 }}>
              <p><b>Step 1:</b> Open this link and enter the code:</p>
              <p>
                <a href={flow.verification_uri} target="_blank" rel="noreferrer">
                  {flow.verification_uri}
                </a>
              </p>
              <h3 style={{ letterSpacing: 2 }}>{flow.user_code}</h3>
              <p style={{ opacity: 0.8 }}>{flow.message}</p>

              <p><b>Step 2:</b> After you complete sign-in, click:</p>
              <button onClick={completeConnect}>I’ve signed in</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
