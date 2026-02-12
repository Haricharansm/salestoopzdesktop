import { useMemo, useState } from "react";

export default function MetricsPanel() {
  const [m] = useState({
    leadsTotal: 120,
    inSequence: 34,
    replied: 11,
    positive: 4,
    negative: 6,
    meetings: 2,
  });

  const cards = useMemo(
    () => [
      { k: "Leads", v: m.leadsTotal },
      { k: "In Sequence", v: m.inSequence },
      { k: "Replies", v: m.replied },
      { k: "Positive", v: m.positive },
      { k: "Negative", v: m.negative },
      { k: "Meetings", v: m.meetings },
    ],
    [m]
  );

  return (
    <div>
      <h2>Outcomes</h2>
      <div className="row">
        {cards.map((c) => (
          <div key={c.k} className="card" style={{ padding: 10, minWidth: 140 }}>
            <div className="mono" style={{ color: "var(--muted)" }}>{c.k}</div>
            <div style={{ fontSize: 20, fontWeight: 800 }}>{c.v}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
