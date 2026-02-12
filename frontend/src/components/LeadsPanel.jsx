import { useState } from "react";
// import { uploadLeads } from "../api";

const DEMO_LEADS = [
  { id: 1, name: "Asha N.", company: "RetailCo", title: "VP Ops", status: "ready" },
  { id: 2, name: "Ben T.", company: "SaaSWorks", title: "Head of Growth", status: "in_sequence" },
  { id: 3, name: "Carla M.", company: "CloudLab", title: "CRO", status: "replied_positive" },
];

export default function LeadsPanel() {
  const [file, setFile] = useState(null);
  const [leads] = useState(DEMO_LEADS);

  const upload = async () => {
    if (!file) return alert("Pick a CSV first.");
    // await uploadLeads(file);
    alert("Uploaded (UI stub). Wire to /leads/upload later.");
  };

  return (
    <div style={{ marginTop: 14 }}>
      <h2>Leads</h2>

      <div className="row">
        <div className="col">
          <label>Upload CSV (name, email, company, title...)</label>
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0])} />
        </div>
        <div className="col" style={{ display: "flex", alignItems: "end" }}>
          <button className="btn" onClick={upload}>Upload</button>
        </div>
      </div>

      <table className="table" style={{ marginTop: 10 }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Company</th>
            <th>Title</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((l) => (
            <tr key={l.id}>
              <td>{l.name}</td>
              <td>{l.company}</td>
              <td>{l.title}</td>
              <td className="mono">{l.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
