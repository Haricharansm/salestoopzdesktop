const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("salestroopz", {
  version: "0.1.0",
});
