import { useState } from "react";
// import { startRun, pauseRun, stopRun } from "../api";

export default function RunControls() {
  const [state, setState] = useState("idle"); // idle | running | paused

  const [config, setConfig] = useState({
    dailyLimit: 80,
    concurrency: 4,
    quietHoursStart: "20:00",
    quietHoursEnd: "07:00",
    stopOnNegative: true,
    autoBookMeeting: true,
  });

  const start = async () => {
    // await startRun(config);
    setState("running");
    alert("Run started (UI stub). Wire to /orchestrator/run/start later.");
  };

  const pause = async () => {
    // await pauseRun();
    setState("paused");
  };

  const stop = async () => {
    // await stopRun();
    setState("idle");
  };

  return (
    <div>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <h2>Run Controls</h2>
        <span className="badge">{state.toUpperCase()}</span>
      </div>

      <div className="row">
        <div className="col">
          <label>Daily Send Limit</label>
          <input
            type="number"
            value={config.dailyLimit}
            onChange={(e) => setConfig({ ...config, dailyLimit: Number(e.target.value) })}
          />
        </div>
        <div className="col">
          <label>Parallel Workers</label>
          <input
            type="number"
            value={config.concurrency}
            onChange={(e) => setConfig({ ...config, concurrency: Number(e.target.value) })}
          />
        </div>
      </div>

      <div className="row">
        <div className="col">
          <label>Quiet Hours Start</label>
          <input
            type="time"
            value={config.quietHoursStart}
            onChange={(e) => setConfig({ ...config, quietHoursStart: e.target.value })}
          />
        </div>
        <div className="col">
          <label>Quiet Hours End</label>
          <input
            type="time"
            value={config.quietHoursEnd}
            onChange={(e) => setConfig({ ...config, quietHoursEnd: e.target.value })}
          />
        </div>
      </div>

      <div className="row">
        <div className="col">
          <label>Stop on negative response</label>
          <select
            value={String(config.stopOnNegative)}
            onChange={(e) => setConfig({ ...config, stopOnNegative: e.target.value === "true" })}
          >
            <option value="true">Yes</option>
            <option value="false">No (manual review)</option>
          </select>
        </div>
        <div className="col">
          <label>Auto-book meeting on positive intent</label>
          <select
            value={String(config.autoBookMeeting)}
            onChange={(e) => setConfig({ ...config, autoBookMeeting: e.target.value === "true" })}
          >
            <option value="true">Yes</option>
            <option value="false">No (request approval)</option>
          </select>
        </div>
      </div>

      <div className="row" style={{ marginTop: 10 }}>
        <button className="btn primary" onClick={start} disabled={state === "running"}>
          Start
        </button>
        <button className="btn" onClick={pause} disabled={state !== "running"}>
          Pause
        </button>
        <button className="btn danger" onClick={stop} disabled={state === "idle"}>
          Stop
        </button>
      </div>

      <p style={{ marginTop: 10 }}>
        This will orchestrate the loop: generate → send → wait → detect reply → branch → repeat until meeting or “no”.
      </p>
    </div>
  );
}
