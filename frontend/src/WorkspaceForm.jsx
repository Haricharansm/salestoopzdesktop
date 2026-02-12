import { useState } from "react";
import { createWorkspace } from "../api";

export default function WorkspaceForm() {
  const [form, setForm] = useState({
    company_name: "",
    industry: "",
    target_persona: "",
    offering: "",
    icp: ""
  });

  const handleSubmit = async () => {
    await createWorkspace(form);
    alert("Workspace saved");
  };

  return (
    <div className="card">
      <h2>Create Workspace</h2>

      {Object.keys(form).map((key) => (
        <input
          key={key}
          placeholder={key}
          value={form[key]}
          onChange={(e) =>
            setForm({ ...form, [key]: e.target.value })
          }
        />
      ))}

      <button onClick={handleSubmit}>Save Workspace</button>
    </div>
  );
}
