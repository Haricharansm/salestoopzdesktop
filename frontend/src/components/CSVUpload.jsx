import { useState } from "react";

const API_BASE = import.meta.env.VITE_AGENT_URL || "http://127.0.0.1:8000";

export default function CSVUpload({ campaignId }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const upload = async () => {
    if (!campaignId) {
      setMessage("⚠️ Please create/select a campaign first");
      return;
    }

    if (!file) {
      setMessage("⚠️ Please choose a CSV file");
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(
        `${API_BASE}/campaign/${campaignId}/leads/upload`,
        {
          method: "POST",
          body: formData
        }
      );

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Upload failed");

      setMessage(`✅ ${data.inserted} leads uploaded`);
      setFile(null);

    } catch (err) {
      setMessage(`❌ ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Upload Leads CSV</h2>

      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={upload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {message && <p style={{ marginTop: 10 }}>{message}</p>}
    </div>
  );
}
