# agent/api_main.py
import os
import uvicorn

from app.db.sqlite import init_db

# IMPORTANT:
# Your FastAPI instance should be defined in agent/main.py as: app = FastAPI(...)
from main import app

def _port() -> int:
    return int(os.getenv("SALESTROOPZ_API_PORT", "8715"))

def main():
    init_db()
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=_port(),
        log_level=os.getenv("SALESTROOPZ_LOG_LEVEL", "info"),
    )

if __name__ == "__main__":
    main()
