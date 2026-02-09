from fastapi import FastAPI
from app.llm.ollama_client import check_ollama, generate_text
from app.db.sqlite import init_db, save_workspace
from app.schemas.models import WorkspaceRequest

app = FastAPI(title="Salestroopz Local Agent")

init_db()

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
