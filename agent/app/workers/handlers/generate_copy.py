import json
from app.db.sqlite import get_session, Campaign, Lead, OutboxEmail
from app.queue.job_queue import enqueue
from app.db.sqlite import log_event

def _dedupe_key(campaign_id: int, lead_id: int, step_index: int) -> str:
    return f"c{campaign_id}:l{lead_id}:s{step_index}"

def handle_generate_copy(payload: dict):
    campaign_id = int(payload["campaign_id"])
    lead_id = int(payload["lead_id"])

    session = get_session()
    c = session.query(Campaign).filter(Campaign.id == campaign_id).first()
    l = session.query(Lead).filter(Lead.id == lead_id).first()
    if not c or not l:
        session.close()
        return

    if l.state not in ["NEW", "FOLLOWUP"]:
        session.close()
        return

    sequence = json.loads(c.sequence_json or "{}")
    steps = sequence.get("steps") or []
    step_index = min(l.touch_count or 0, max(0, len(steps) - 1))
    if not steps:
        session.close()
        raise RuntimeError("No sequence steps saved for campaign")

    # NOTE: placeholder copy generation for now (next: call RunnerAgent + Ollama)
    step = steps[step_index]
    subject = step.get("subject") or f"Quick question, {l.full_name.split(' ')[0] if l.full_name else ''}"
    body = step.get("body") or f"Hi {l.full_name or ''},\n\nWanted to reach out about {c.name}.\n\n— Taylor"

    dk = _dedupe_key(campaign_id, lead_id, step_index)

    # Idempotency: if outbox exists, don't recreate
    existing = session.query(OutboxEmail).filter(OutboxEmail.dedupe_key == dk).first()
    if existing:
        session.close()
        enqueue("send_email", {"outbox_id": existing.id})
        return

    row = OutboxEmail(
        campaign_id=campaign_id,
        lead_id=lead_id,
        step_index=step_index,
        dedupe_key=dk,
        subject=subject,
        body=body,
        status="queued",
        provider="m365",
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    session.close()

    log_event("outbox.created", campaign_id=campaign_id, lead_id=lead_id, message=f"Outbox queued step {step_index}")
    enqueue("send_email", {"outbox_id": row.id})
