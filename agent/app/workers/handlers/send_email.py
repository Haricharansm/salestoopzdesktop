from datetime import datetime, timedelta
from app.db.sqlite import get_session, OutboxEmail, Lead, Campaign
from app.queue.job_queue import enqueue
from app.db.sqlite import log_event, log_activity

def handle_send_email(payload: dict):
    outbox_id = int(payload["outbox_id"])

    session = get_session()
    ob = session.query(OutboxEmail).filter(OutboxEmail.id == outbox_id).first()
    if not ob:
        session.close()
        return

    if ob.status == "sent":
        session.close()
        return

    lead = session.query(Lead).filter(Lead.id == ob.lead_id).first()
    camp = session.query(Campaign).filter(Campaign.id == ob.campaign_id).first()
    if not lead or not camp:
        session.close()
        return

    # TODO: Replace with actual M365 send returning message_id/thread_id
    fake_message_id = f"local-{ob.dedupe_key}"
    fake_thread_id = lead.conversation_id or fake_message_id

    ob.status = "sent"
    ob.provider_message_id = fake_message_id
    ob.thread_id = fake_thread_id
    ob.sent_at = datetime.utcnow()

    # advance lead state
    lead.touch_count = (lead.touch_count or 0) + 1
    lead.state = "WAITING_REPLY"
    lead.conversation_id = fake_thread_id
    lead.next_touch_at = datetime.utcnow() + timedelta(days=camp.cadence_days)

    session.commit()
    session.close()

    log_event("email.sent", campaign_id=camp.id, lead_id=lead.id, message=f"Sent step {ob.step_index}")
    log_activity(lead.id, "email_sent", f"Sent: {ob.subject}")

    # schedule reply polling soon
    enqueue("poll_replies", {"campaign_id": camp.id, "lead_id": lead.id}, run_at=(datetime.utcnow() + timedelta(seconds=30)))
