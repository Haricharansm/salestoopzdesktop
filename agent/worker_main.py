# agent/worker_main.py
import os
from app.db.sqlite import init_db, log_event

# You will create app/workers/runner.py with run_forever()
# (If you already have it elsewhere, update the import below.)
from app.workers.runner import run_forever

def main():
    init_db()
    log_event("runner.boot", message="Runner starting (worker_main)")
    run_forever(poll_interval=float(os.getenv("SALESTROOPZ_RUNNER_POLL", "0.5")))

if __name__ == "__main__":
    main()
