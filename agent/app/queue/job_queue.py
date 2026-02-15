import json
import socket
import os
from datetime import datetime, timedelta
from app.db.sqlite import get_session, JobQueue
from app.db.sqlite import log_event  # we'll add this helper below

LEASE_SECONDS_DEFAULT = 60

def _owner_id() -> str:
    return f"{socket.gethostname()}:{os.getpid()}"

def enqueue(job_type: str, payload: dict, run_at: datetime | None = None, max_attempts: int = 8) -> int:
    session = get_session()
    row = JobQueue(
        job_type=job_type,
        status="queued",
        run_at=run_at or datetime.utcnow(),
        attempts=0,
        max_attempts=max_attempts,
        payload_json=json.dumps(payload),
        updated_at=datetime.utcnow(),
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    session.close()
    return row.id

def claim_next_job(lease_seconds: int = LEASE_SECONDS_DEFAULT) -> JobQueue | None:
    """
    Claim the next due job by taking a lease. Crash-safe: expired leases can be reclaimed.
    """
    session = get_session()
    now = datetime.utcnow()
    owner = _owner_id()
    lease_expires = now + timedelta(seconds=lease_seconds)

    # Find candidate
    job = (
        session.query(JobQueue)
        .filter(JobQueue.status.in_(["queued", "running"]))
        .filter(JobQueue.run_at <= now)
        .filter((JobQueue.lease_expires_at == None) | (JobQueue.lease_expires_at <= now))
        .order_by(JobQueue.run_at.asc(), JobQueue.id.asc())
        .first()
    )

    if not job:
        session.close()
        return None

    # Claim by setting lease
    job.status = "running"
    job.lease_owner = owner
    job.lease_expires_at = lease_expires
    job.updated_at = now
    session.commit()
    session.refresh(job)
    session.close()

    log_event("job.claimed", job_id=job.id, message=f"Claimed {job.job_type}", data={"owner": owner})
    return job

def mark_done(job_id: int):
    session = get_session()
    job = session.query(JobQueue).filter(JobQueue.id == job_id).first()
    if not job:
        session.close()
        return
    job.status = "done"
    job.lease_expires_at = None
    job.updated_at = datetime.utcnow()
    session.commit()
    session.close()
    log_event("job.done", job_id=job_id)

def mark_failed(job_id: int, err: str, retry_at: datetime | None):
    session = get_session()
    job = session.query(JobQueue).filter(JobQueue.id == job_id).first()
    if not job:
        session.close()
        return

    job.attempts = (job.attempts or 0) + 1
    job.last_error = err
    job.updated_at = datetime.utcnow()
    job.lease_expires_at = None

    if job.attempts >= (job.max_attempts or 8):
        job.status = "failed"
        session.commit()
        session.close()
        log_event("job.failed", level="ERROR", job_id=job_id, message=err)
        return

    job.status = "queued"
    job.run_at = retry_at or (datetime.utcnow() + timedelta(seconds=10))
    session.commit()
    session.close()
    log_event("job.retry_scheduled", level="WARN", job_id=job_id, message=err, data={"attempts": job.attempts, "run_at": job.run_at.isoformat()})
