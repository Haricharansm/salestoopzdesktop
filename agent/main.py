from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.llm.ollama_client import check_ollama, generate_text
from app.db.sqlite import init_db, save_workspace
from app.schemas.models import WorkspaceRequest

from app.m365.auth import M365Auth
from app.m365.client import M365Client

app = FastAPI(title="Salestroopz Local Agent")
init_db()

# --- M365 setup ---
try:
    m365_auth = M365Auth()
except Exception:
    m365_auth = None

_device_flow_holder = {"flow": None}

class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

@app.get("/health")
def health():
    return {"status": "agent running"}

@app.get("/ollama/status")
def ollama_status():
    return {"ollama_running": check_ollama()}

@app.post("/workspace")
def create_workspace(data: WorkspaceRequest):
    save_workspace(data)
    return {"message": "Workspace saved locally"}

@app.post("/campaign/generate")
def generate_campaign(prompt: str):
    result = generate_text(prompt)
    return {"campaign_text": result}

# ------------------- M365 endpoints -------------------

@app.get("/m365/status")
def m365_status():
    if not m365_auth:
        return {"connected": False, "error": "M365 not configured. Set M365_CLIENT_ID."}

    token = m365_auth.acquire_token_silent()
    if not token or "access_token" not in token:
        return {"connected": False}

    client = M365Client(token["access_token"])
    me = client.me()
    return {"connected": True, "user": {"displayName": me.get("displayName"), "mail": me.get("mail")}}

@app.post("/m365/device/start")
def m365_device_start():
    if not m365_auth:
        raise HTTPException(status_code=500, detail="M365 not configured. Set M365_CLIENT_ID.")

    flow = m365_auth.start_device_flow()
    _device_flow_holder["flow"] = flow
    return {
        "user_code": flow["user_code"],
        "verification_uri": flow["verification_uri"],
        "message": flow["message"],
    }

@app.post("/m365/device/complete")
def m365_device_complete():
    if not m365_auth:
        raise HTTPException(status_code=500, detail="M365 not configured. Set M365_CLIENT_ID.")

    flow = _device_flow_holder.get("flow")
    if not flow:
        raise HTTPException(status_code=400, detail="No device flow started")

    token = m365_auth.complete_device_flow(flow)
    if "access_token" not in token:
        raise HTTPException(status_code=401, detail=str(token))

    # Clear flow after success
    _device_flow_holder["flow"] = None
    return {"connected": True}

@app.post("/m365/send")
def m365_send(req: SendEmailRequest):
    if not m365_auth:
        raise HTTPException(status_code=500, detail="M365 not configured. Set M365_CLIENT_ID.")

    token = m365_auth.acquire_token_silent()
    if not token or "access_token" not in token:
        raise HTTPException(status_code=401, detail="Not connected to Microsoft 365")

    client = M365Client(token["access_token"])
    client.send_mail(req.to_email, req.subject, req.body)
    return {"sent": True}
