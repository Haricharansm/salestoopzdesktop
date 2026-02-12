import { useState } from "react";
import { generateCampaign } from "../api";

export default function CampaignForm() {
  const [prompt, setPrompt] = useState("");

  const runCampaign = async () => {
    const res = await generateCampaign(prompt);
    alert(JSON.stringify(res.data, null, 2));
  };

  return (
    <div className="card">
      <h2>Launch Campaign</h2>

      <textarea
        rows="3"
        placeholder="Describe campaign goal"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <button onClick={runCampaign}>Generate Campaign</button>
    </div>
  );
}
components/
