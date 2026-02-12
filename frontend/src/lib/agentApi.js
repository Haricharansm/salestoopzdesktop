function ensureBridge() {
  if (!window?.salestroopz?.agent) {
    throw new Error("Electron preload bridge not found. (window.salestroopz.agent)");
  }
  return window.salestroopz.agent;
}

export const agentApi = {
  version: () => window?.salestroopz?.version ?? "unknown",

  health: async () => ensureBridge().health(),
  ollamaStatus: async () => ensureBridge().ollamaStatus(),

  createWorkspace: async (payload) => ensureBridge().createWorkspace(payload),
  generateCampaign: async (prompt) => ensureBridge().generateCampaign(prompt),
};
