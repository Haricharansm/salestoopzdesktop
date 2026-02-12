import { useEffect, useMemo, useState } from "react";
import SequenceBuilder from "./SequenceBuilder";
import LeadsPanel from "./LeadsPanel";
import RunControls from "./RunControls";
import ActivityPanel from "./ActivityPanel";
import MetricsPanel from "./MetricsPanel";
import { ollamaStatus } from "../api";

export default function OrchestrationDashboard() {
  const [ollamaOk, setOllamaOk] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await ollamaStatus();
        setOllamaOk(!!res.data?.ollama_running);
      } catch {
        setOllamaOk(false);
      }
    })();
  }, []);

  const healthBadge = useMemo(() => {
    if (ollamaOk === null) return <span className="badge">Checking LLM…</span>;
    if (ollamaOk) return <span className="badge good">Ollama Running</span>;
    return <span className="badge warn">Ollama Not Reachable</span>;
  }, [ollamaOk]);

  return (
    <div className="grid" style={{ marginTop: 14 }}>
      <div className="card">
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <h2>Autonomous Orchestration</h2>
          {healthBadge}
        </div>

        <SequenceBuilder />
        <div style={{ height: 12 }} />
        <LeadsPanel />
      </div>

      <div className="card">
        <RunControls />
        <div style={{ height: 12 }} />
        <MetricsPanel />
        <div style={{ height: 12 }} />
        <ActivityPanel />
      </div>
    </div>
  );
}
