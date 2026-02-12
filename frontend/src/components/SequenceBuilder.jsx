import { useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_AGENT_URL || "http://127.0.0.1:8000";

const DEFAULT_STEPS = [
  { id: "s1", channel: "email", delayHours: 0, subject: "Quick question", body: "Hi {{first_name}} — …", stopOnReply: true },
  { id: "s2", channel: "email", delayHours: 48, subject: "Following up", body: "Bumping this in case you missed it…", stopOnReply: true },
  { id: "s3", channel: "linkedin", delayHours: 24, subject: "", body: "Sent you a quick note here as well…", stopOnReply: true },
];

export default function SequenceBuilder({ campaignId, onCampaignReady }) {
  const [sequenceName, setSequenceName] = useState("Default Multi-touch");
  const [steps, setSteps] = useState(DEFAULT_STEPS);

  const [stopRule, setStopRule] = useState("stop_on_negative");
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");

  const channels = useMemo(() => ["email", "linkedin", "call", "sms"], []);

  const addStep = () => {
    setSteps((prev) => [
      ...prev,
      {
        id: `s${prev.length + 1}`,
        channel: "email",
        delayHours: 24,
        subject: "",
        body: "",
        stopOnReply: true,
      },
    ]);
  };

  const updateStep = (idx, patch) => {
    setSteps((prev) => prev.map((s, i) => (i === idx ? { ...s, ...patch } : s)));
  };

  const removeStep = (idx) => setSteps((prev) => prev.filter((_, i) => i !== idx));

  const ensureCampaign = async () => {
    if (campaignId) return campaignId;

    const res = await fetch(`${API_BASE}/campaign`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: sequenceName,
        cadence_days: 3,
        max_touches: 4,
      }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data?.detail || "Failed to create campaign");

    const id = data.campaign_id;
    onCampaignReady?.(id);
    return id;
  };

  const save = async () => {
    try {
      setSaving(true);
      setStatusMsg("");

      const id = await ensureCampaign();

      const res = await fetch(`${API_BASE}/campaign/${id}/sequence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: sequenceName,
          stop_rule: stopRule,
          steps,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Failed to save sequence");

      setStatusMsg(`✅ Saved sequence to campaign #${id}`);
    } catch (e) {
      setStatusMsg(`❌ ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="row" style={{ marginTop: 10 }}>
        <div className="col">
          <label>Sequence Name</label>
          <input value={sequenceName} onChange={(e) => setSequenceName(e.target.value)} />
        </div>
        <div className="col">
          <label>Stop Rules</label>
          <select value={stopRule} onChange={(e) => setStopRule(e.target.value)}>
            <option value="stop_on_negative">Stop on negative reply</option>
            <option value="keep_trying">Keep trying unless “stop”</option>
          </select>
        </div>
      </div>

      <div style={{ marginTop: 8 }}>
        {campaignId ? (
          <p>
            Campaign: <span className="mono">#{campaignId}</span>
          </p>
        ) : (
          <p style={{ opacity: 0.8 }}>No campaign yet — it will be created on first save.</p>
        )}
        {statusMsg ? <p style={{ marginTop: 6 }}>{statusMsg}</p> : null}
      </div>

      <div style={{ marginTop: 10 }}>
        <h2>Touchpoints</h2>

        {steps.map((s, idx) => (
          <div key={s.id} className="card" style={{ padding: 12, marginBottom: 10 }}>
            <div className="row">
              <div className="col">
                <label>Channel</label>
                <select value={s.channel} onChange={(e) => updateStep(idx, { channel: e.target.value })}>
                  {channels.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
              <div className="col">
                <label>Delay (hours after previous)</label>
                <input
                  type="number"
                  value={s.delayHours}
                  onChange={(e) => updateStep(idx, { delayHours: Number(e.target.value) })}
                />
              </div>
              <div className="col">
                <label>Stop on reply</label>
                <select
                  value={String(s.stopOnReply)}
                  onChange={(e) => updateStep(idx, { stopOnReply: e.target.value === "true" })}
                >
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              </div>
            </div>

            {s.channel === "email" ? (
              <>
                <label style={{ marginTop: 8 }}>Subject</label>
                <input value={s.subject} onChange={(e) => updateStep(idx, { subject: e.target.value })} />
              </>
            ) : null}

            <label style={{ marginTop: 8 }}>Message</label>
            <textarea value={s.body} onChange={(e) => updateStep(idx, { body: e.target.value })} />

            <div className="row" style={{ marginTop: 10 }}>
              <button className="btn" onClick={() => removeStep(idx)}>
                Remove
              </button>
            </div>
          </div>
        ))}

        <div className="row">
          <button className="btn" onClick={addStep}>
            + Add Touchpoint
          </button>
          <button className="btn primary" onClick={save} disabled={saving}>
            {saving ? "Saving..." : "Save Sequence"}
          </button>
        </div>

        <p style={{ marginTop: 8 }}>
          Tip: Use tokens like <span className="mono">{"{{first_name}}"}</span>,{" "}
          <span className="mono">{"{{company}}"}</span>, <span className="mono">{"{{pain_point}}"}</span>.
        </p>
      </div>
    </div>
  );
}
