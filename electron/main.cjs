const { app, BrowserWindow, shell } = require("electron");
const path = require("path");
const http = require("http");

let mainWindow;

const DEV_URL = "http://localhost:5173";
const PROD_INDEX = path.join(__dirname, "..", "frontend", "dist", "index.html");

function waitForDevServer(url, timeoutMs = 15000) {
  const start = Date.now();

  return new Promise((resolve, reject) => {
    const tryOnce = () => {
      http
        .get(url, (res) => {
          // Any 2xx/3xx means server is alive
          if (res.statusCode && res.statusCode >= 200 && res.statusCode < 400) {
            res.resume();
            return resolve(true);
          }
          res.resume();
          retry();
        })
        .on("error", retry);
    };

    const retry = () => {
      if (Date.now() - start > timeoutMs) {
        return reject(new Error(`Dev server not ready at ${url} within ${timeoutMs}ms`));
      }
      setTimeout(tryOnce, 300);
    };

    tryOnce();
  });
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: "Salestroopz Desktop",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  // Open external links in default browser, not inside Electron window
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  const isDev = !app.isPackaged;

  if (isDev) {
    try {
      await waitForDevServer(DEV_URL);
      await mainWindow.loadURL(DEV_URL);
      mainWindow.webContents.openDevTools({ mode: "detach" });
    } catch (err) {
      await mainWindow.loadURL(
        `data:text/html,
         <h2>Vite dev server not running</h2>
         <p>Start it with: <code>npm run dev</code></p>
         <pre>${String(err).replace(/</g, "&lt;")}</pre>`
      );
    }
  } else {
    await mainWindow.loadFile(PROD_INDEX);
  }
}

app.whenReady().then(async () => {
  await createWindow();

  app.on("activate", async () => {
    if (BrowserWindow.getAllWindows().length === 0) await createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
