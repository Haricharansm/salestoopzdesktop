from app.db.sqlite import get_session, Lead
from app.db.sqlite import log_event

def handle_poll_replies(payload: dict):
    lead_id = int(payload["lead_id"])

    session = get_session()
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        return

    # TODO: call M365 replies API and classify
    # For now: do nothing
    session.close()
    log_event("replies.polled", lead_id=lead_id, message="Polled replies (stub)")
