import { useMemo, useState } from "react";
// import { saveSequence } from "../api";

const DEFAULT_STEPS = [
  { id: "s1", channel: "email", delayHours: 0, subject: "Quick question", body: "Hi {{first_name}} — …", stopOnReply: true },
  { id: "s2", channel: "email", delayHours: 48, subject: "Following up", body: "Bumping this in case you missed it…", stopOnReply: true },
  { id: "s3", channel: "linkedin", delayHours: 24, subject: "", body: "Sent you a quick note here as well…", stopOnReply: true },
];

export default function SequenceBuilder() {
  const [sequenceName, setSequenceName] = useState("Default Multi-touch");
  const [steps, setSteps] = useState(DEFAULT_STEPS);

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

  const save = async () => {
    // UI-first. Wire later:
    // await saveSequence({ name: sequenceName, steps });
    alert("Sequence saved (UI stub). Wire to /orchestrator/sequence later.");
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
          <select defaultValue="stop_on_negative">
            <option value="stop_on_negative">Stop on negative reply</option>
            <option value="keep_trying">Keep trying unless “stop”</option>
          </select>
        </div>
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
                    <option key={c} value={c}>{c}</option>
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
              <button className="btn" onClick={() => removeStep(idx)}>Remove</button>
            </div>
          </div>
        ))}

        <div className="row">
          <button className="btn" onClick={addStep}>+ Add Touchpoint</button>
          <button className="btn primary" onClick={save}>Save Sequence</button>
        </div>

        <p style={{ marginTop: 8 }}>
          Tip: Use tokens like <span className="mono">{"{{first_name}}"}</span>, <span className="mono">{"{{company}}"}</span>, <span className="mono">{"{{pain_point}}"}</span>.
        </p>
      </div>
    </div>
  );
}
