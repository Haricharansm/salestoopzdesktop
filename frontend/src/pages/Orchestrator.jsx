import React, { useMemo, useState } from "react";
import { agentApi } from "../lib/agentApi";

function parseCSV(text) {
  // simple CSV parser: expects headers in first row
  // supports commas inside quotes in a basic way
  const rows = [];
  let cur = "", inQuotes = false;
  const lines = [];
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (ch === '"' && text[i - 1] !== "\\") inQuotes = !inQuotes;
    if (ch === "\n" && !inQuotes) {
      lines.push(cur);
      cur = "";
    } else {
      cur += ch;
    }
  }
  if (cur.trim()) lines.push(cur);

  const splitRow = (line) => {
    const out = [];
    let s = "", q = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (c === '"' && line[i - 1] !== "\\") q = !q;
      else if (c === "," && !q) {
        out.push(s.trim().replace(/^"|"$/g, ""));
        s = "";
      } else s += c;
    }
    out.push(s.trim().replace(/^"|"$/g, ""));
    return out;
  };

  const header = splitRow(lines[0] || "").map((h) => h.trim());
  for (let i = 1; i < lines.length; i++) {
    const cols = splitRow(lines[i]);
    const obj = {};
    header.forEach((h, idx) => (obj[h] = cols[idx] ?? ""));
    if (Object.values(obj).some((v) => String(v).trim() !== "")) rows.push(obj);
  }
  return rows;
}

const Badge = ({ children }) => (
  <span style={{
    fontSize: 12, padding: "4px 8px", borderRadius: 999,
    background: "#f2f2f2", display: "inline-block"
  }}>{children}</span>
);

const Step = ({ title, status, note }) => (
  <div style={{
    border: "1px solid #eee", borderRadius: 12, padding: 12, marginBottom: 10
  }}>
    <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
      <div style={{ fontWeight: 600 }}>{title}</div>
      <Badge>{status}</Badge>
    </div>
    {note ? <div style={{ marginTop: 8, color: "#666", fontSize: 13 }}>{note}</div> : null}
  </div>
);

export default function Orchestrator() {
  const [csvName, setCsvName] = useState("");
  const [leads, setLeads] = useState([]);
  const [workspace, setWorkspace] = useState({
    offering: "",
    target_persona: "",
    icp: "",
  });

  const [run, setRun] = useState(null); // {id, startedAt, steps:[], result}
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const [campaignPrompt, setCampaignPrompt] = useState(
    "Create a 6-step outbound email sequence with a warm, human tone. Include subject lines and CTAs."
  );

  const leadPreview = useMemo(() => leads.slice(0, 8), [leads]);

  async function checkDeps() {
    setError("");
    const [health, ollama] = await Promise.all([
      agentApi.health().catch((e) => ({ error: e.message })),
      agentApi.ollamaStatus().catch((e) => ({ error: e.message })),
    ]);
    return { health, ollama };
  }

  async function onUpload(e) {
    setError("");
    const file = e.target.files?.[0];
    if (!file) return;
    setCsvName(file.name);
    const text = await file.text();
    const rows = parseCSV(text);
    setLeads(rows);
  }

  async function startRun() {
    setError("");
    setBusy(true);

    const runId = `run_${Date.now()}`;
    const startedAt = new Date().toISOString();

    const steps = [
      { title: "Dependency check (FastAPI + Ollama)", status: "running", note: "" },
      { title: "Validate inputs (workspace + leads)", status: "queued", note: "" },
      { title: "Generate multi-touch campaign", status: "queued", note: "" },
      { title: "Prepare per-lead plan (draft → send → follow-up)", status: "queued", note: "" },
      { title: "Start execution loop", status: "queued", note: "Execution engine will be implemented next." },
    ];

    setRun({ id: runId, startedAt, steps, result: null });

    try {
      // Step 1: deps
      const deps = await checkDeps();
      setRun((r) => ({
        ...r,
        steps: r.steps.map((s, idx) =>
          idx === 0
            ? {
                ...s,
                status:
                  deps.health?.error || deps.ollama?.error
                    ? "failed"
                    : "done",
                note:
                  deps.health?.error
                    ? `FastAPI error: ${deps.health.error}`
                    : deps.ollama?.error
                    ? `Ollama error: ${deps.ollama.error}`
                    : "FastAPI reachable and Ollama running.",
              }
            : s
        ),
      }));

      if (deps.health?.error || deps.ollama?.error) {
        throw new Error("Dependency check failed. Fix FastAPI/Ollama and retry.");
      }

      // Step 2: validate inputs
      const missing = [];
      if (!workspace.offering.trim()) missing.push("offering");
      if (!workspace.target_persona.trim()) missing.push("target_persona");
      if (!workspace.icp.trim()) missing.push("icp");
      if (!leads.length) missing.push("leads (CSV upload)");

      setRun((r) => ({
        ...r,
        steps: r.steps.map((s, idx) =>
          idx === 1
            ? {
                ...s,
                status: missing.length ? "failed" : "done",
                note: missing.length ? `Missing: ${missing.join(", ")}` : "Inputs look good.",
              }
            : s
        ),
      }));

      if (missing.length) throw new Error(`Missing required inputs: ${missing.join(", ")}`);

      // Step 3: create workspace (optional but recommended)
      // Your backend expects company_name/industry too; keep defaults for now.
      await agentApi.createWorkspace({
        company_name: "Saxon.AI",
        industry: "Enterprise AI Consulting",
        target_persona: workspace.target_persona,
        offering: workspace.offering,
        icp: workspace.icp,
      });

      // Step 3: generate campaign
      setRun((r) => ({
        ...r,
        steps: r.steps.map((s, idx) => (idx === 2 ? { ...s, status: "running" } : s)),
      }));

      const generated = await agentApi.generateCampaign(campaignPrompt);

      setRun((r) => ({
        ...r,
        steps: r.steps.map((s, idx) => (idx === 2 ? { ...s, status: "done", note: "Campaign generated." } : s)),
        result: generated,
      }));

      // Step 4: per-lead plan
      setRun((r) => ({
        ...r,
        steps: r.steps.map((s, idx) =>
          idx === 3 ? { ...s, status: "done", note: `Prepared plan for ${leads.length} leads (UI-only for now).` } : s
        ),
      }));

      // Step 5: execution loop placeholder
      setRun((r) => ({
        ...r,
        steps: r.steps.map((s, idx) =>
          idx === 4
            ? {
                ...s,
                status: "blocked",
                note:
                  "Next: implement Microsoft 365 sending + inbox monitoring + follow-up scheduling (agent-side).",
              }
            : s
        ),
      }));
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ padding: 20, maxWidth: 1200, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h2 style={{ margin: 0 }}>Autonomous Orchestration</h2>
        <div style={{ color: "#666", fontSize: 13 }}>Agent: 127.0.0.1:8000 • UI v{agentApi.version()}</div>
      </div>

      {error ? (
        <div style={{ marginTop: 12, padding: 12, borderRadius: 12, background: "#fff3f3", border: "1px solid #ffd2d2" }}>
          <b>Error:</b> {error}
        </div>
      ) : null}

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 16, marginTop: 16 }}>
        {/* Left: Inputs */}
        <div style={{ border: "1px solid #eee", borderRadius: 16, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Inputs</h3>

          <label style={{ display: "block", fontSize: 13, color: "#555", marginBottom: 6 }}>Offering</label>
          <textarea
            value={workspace.offering}
            onChange={(e) => setWorkspace((w) => ({ ...w, offering: e.target.value }))}
            placeholder="e.g., Salestroopz — AI SDR that runs outreach, follow-ups, and meeting booking end-to-end."
            rows={3}
            style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #ddd" }}
          />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 12 }}>
            <div>
              <label style={{ display: "block", fontSize: 13, color: "#555", marginBottom: 6 }}>Target persona</label>
              <input
                value={workspace.target_persona}
                onChange={(e) => setWorkspace((w) => ({ ...w, target_persona: e.target.value }))}
                placeholder="VP Sales / Head of Growth / CIO"
                style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #ddd" }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: 13, color: "#555", marginBottom: 6 }}>ICP</label>
              <input
                value={workspace.icp}
                onChange={(e) => setWorkspace((w) => ({ ...w, icp: e.target.value }))}
                placeholder="Mid-market SaaS, 50–500 reps…"
                style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #ddd" }}
              />
            </div>
          </div>

          <div style={{ marginTop: 14 }}>
            <label style={{ display: "block", fontSize: 13, color: "#555", marginBottom: 6 }}>Leads (CSV upload)</label>
            <input type="file" accept=".csv,text/csv" onChange={onUpload} />
            <div style={{ marginTop: 8, color: "#666", fontSize: 13 }}>
              {csvName ? (
                <>
                  Loaded <b>{csvName}</b> • <b>{leads.length}</b> leads
                </>
              ) : (
                "Upload a CSV with headers (e.g., first_name, last_name, email, company, title)."
              )}
            </div>

            {leadPreview.length ? (
              <div style={{ marginTop: 10, border: "1px solid #eee", borderRadius: 12, padding: 10 }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>Preview</div>
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                    <thead>
                      <tr>
                        {Object.keys(leadPreview[0]).slice(0, 5).map((h) => (
                          <th key={h} style={{ textAlign: "left", padding: 6, borderBottom: "1px solid #eee" }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {leadPreview.map((row, idx) => (
                        <tr key={idx}>
                          {Object.keys(leadPreview[0]).slice(0, 5).map((h) => (
                            <td key={h} style={{ padding: 6, borderBottom: "1px solid #f4f4f4" }}>
                              {String(row[h] ?? "").slice(0, 40)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : null}
          </div>

          <div style={{ marginTop: 14 }}>
            <label style={{ display: "block", fontSize: 13, color: "#555", marginBottom: 6 }}>
              Campaign generation prompt
            </label>
            <textarea
              value={campaignPrompt}
              onChange={(e) => setCampaignPrompt(e.target.value)}
              rows={4}
              style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #ddd" }}
            />
          </div>

          <button
            onClick={startRun}
            disabled={busy}
            style={{
              marginTop: 14,
              width: "100%",
              padding: "12px 14px",
              borderRadius: 12,
              border: "1px solid #111",
              background: busy ? "#eee" : "#111",
              color: busy ? "#666" : "#fff",
              fontWeight: 700,
              cursor: busy ? "not-allowed" : "pointer",
            }}
          >
            {busy ? "Running…" : "Start autonomous run (Phase 1)"}
          </button>

          <div style={{ marginTop: 10, fontSize: 12, color: "#777" }}>
            Phase 1: validate + generate campaign + prep plan. Next phase: M365 send + inbox watch + follow-ups.
          </div>
        </div>

        {/* Right: Run timeline + output */}
        <div style={{ border: "1px solid #eee", borderRadius: 16, padding: 16 }}>
          <h3 style={{ marginTop: 0 }}>Run</h3>

          {!run ? (
            <div style={{ color: "#666" }}>
              Start a run to see step-by-step orchestration, outputs, and debug payloads.
            </div>
          ) : (
            <>
              <div style={{ fontSize: 13, color: "#666", marginBottom: 10 }}>
                <b>{run.id}</b> • {run.startedAt}
              </div>

              {run.steps.map((s, idx) => (
                <Step key={idx} title={s.title} status={s.status} note={s.note} />
              ))}

              <div style={{ marginTop: 14 }}>
                <h4 style={{ margin: "10px 0" }}>Generated campaign (raw)</h4>
                <pre style={{
                  background: "#0b0b0b",
                  color: "#d6f5d6",
                  padding: 12,
                  borderRadius: 12,
                  overflowX: "auto",
                  fontSize: 12
                }}>
{run.result ? JSON.stringify(run.result, null, 2) : "// No output yet"}
                </pre>
              </div>

              <div style={{ marginTop: 12 }}>
                <h4 style={{ margin: "10px 0" }}>Debug: workspace payload</h4>
                <pre style={{
                  background: "#f7f7f7",
                  padding: 12,
                  borderRadius: 12,
                  overflowX: "auto",
                  fontSize: 12
                }}>
{JSON.stringify({
  company_name: "Saxon.AI",
  industry: "Enterprise AI Consulting",
  target_persona: workspace.target_persona,
  offering: workspace.offering,
  icp: workspace.icp
}, null, 2)}
                </pre>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
