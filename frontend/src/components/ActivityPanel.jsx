import { useMemo, useState } from "react";

export default function ActivityPanel() {
  const [events] = useState([
    { ts: "19:58", level: "info", msg: "Run started: concurrency=4, dailyLimit=80" },
    { ts: "20:01", level: "info", msg: "Generated email #1 for Ben T. (SaaSWorks)" },
    { ts: "20:02", level: "info", msg: "Sent email to ben@saasworks.com" },
    { ts: "20:10", level: "warn", msg: "Throttle: reached quiet hours, pausing sends" },
    { ts: "08:05", level: "good", msg: "Positive reply detected from Carla M. → proposing calendar slots" },
  ]);

  const lines = useMemo(() => {
    return events
      .map((e) => {
        const tag = e.level === "good" ? "OK" : e.level === "warn" ? "WARN" : "INFO";
        return `[${e.ts}] ${tag}  ${e.msg}`;
      })
      .join("\n");
  }, [events]);

  return (
    <div>
      <h2>Live Activity</h2>
      <div className="log">
        <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{lines}</pre>
        <div className="muted" style={{ marginTop: 8 }}>
          (UI demo feed — wire to /orchestrator/activity for realtime.)
        </div>
      </div>
    </div>
  );
}
