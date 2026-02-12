import axios from "axios";

const API = import.meta.env.VITE_API_BASE_URL;

// Workspace (you already have /workspace)
export const createWorkspace = (data) => axios.post(`${API}/workspace`, data);

// Leads (UI-first; wire these to backend later)
export const uploadLeads = (file) => {
  const form = new FormData();
  form.append("file", file);
  return axios.post(`${API}/leads/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const listLeads = () => axios.get(`${API}/leads`);

// Orchestration (new endpoints you’ll add later)
export const saveSequence = (sequence) => axios.post(`${API}/orchestrator/sequence`, sequence);
export const getSequence = () => axios.get(`${API}/orchestrator/sequence`);

export const startRun = (runConfig) => axios.post(`${API}/orchestrator/run/start`, runConfig);
export const pauseRun = () => axios.post(`${API}/orchestrator/run/pause`);
export const stopRun = () => axios.post(`${API}/orchestrator/run/stop`);
export const runStatus = () => axios.get(`${API}/orchestrator/run/status`);

export const activityFeed = () => axios.get(`${API}/orchestrator/activity`);
export const metrics = () => axios.get(`${API}/orchestrator/metrics`);

// Health
export const ollamaStatus = () => axios.get(`${API}/ollama/status`);
