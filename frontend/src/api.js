import axios from "axios";

const API = import.meta.env.VITE_API_BASE_URL;

export const createWorkspace = (data) =>
  axios.post(`${API}/workspace`, data);

export const generateCampaign = (prompt) =>
  axios.post(`${API}/campaign/generate?prompt=${prompt}`);

export const ollamaStatus = () =>
  axios.get(`${API}/ollama/status`);
