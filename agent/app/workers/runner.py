import time
import json
from datetime import datetime, timedelta
from app.queue.job_queue import claim_next_job, mark_done, mark_failed
from app.db.sqlite import log_event

# Import handlers
from app.workers.handlers.generate_copy import handle_generate_copy
from app.workers.handlers.send_email import handle_send_email
from app.workers.handlers.poll_replies import handle_poll_replies
from app.workers.handlers.tick import handle_tick

HANDLERS = {
    "tick": handle_tick,
    "generate_copy": handle_generate_copy,
    "send_email": handle_send_email,
    "poll_replies": handle_poll_replies,
}

def backoff_seconds(attempt: int) -> int:
    # 1,2,4,8,16,30,60...
    return min(60, 2 ** max(0, attempt - 1))

def run_forever(poll_interval: float = 0.5):
    log_event("runner.started", message="Runner loop started")

    while True:
        job = claim_next_job()
        if not job:
            time.sleep(poll_interval)
            continue

        try:
            payload = json.loads(job.payload_json or "{}")
            handler = HANDLERS.get(job.job_type)
            if not handler:
                raise RuntimeError(f"No handler for job_type={job.job_type}")

            handler(payload)  # handlers should be idempotent
            mark_done(job.id)

        except Exception as e:
            retry_at = datetime.utcnow() + timedelta(seconds=backoff_seconds((job.attempts or 0) + 1))
            mark_failed(job.id, err=str(e), retry_at=retry_at)

if __name__ == "__main__":
    run_forever()
