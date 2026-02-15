from datetime import datetime, timedelta
from app.queue.job_queue import enqueue
from app.db.sqlite import get_session, Campaign, Lead

def handle_tick(payload: dict):
    """
    Periodically enqueue work for running campaigns.
    """
    session = get_session()
    now = datetime.utcnow()

    campaigns = session.query(Campaign).filter(Campaign.status == "running").all()
    for c in campaigns:
        # enqueue generate_copy jobs for due leads
        due_leads = (
            session.query(Lead)
            .filter(Lead.campaign_id == c.id)
            .filter(Lead.next_touch_at <= now)
            .filter(Lead.state.in_(["NEW", "FOLLOWUP"]))
            .limit(25)
            .all()
        )
        for lead in due_leads:
            enqueue("generate_copy", {"campaign_id": c.id, "lead_id": lead.id})

    session.close()

    # schedule next tick
    enqueue("tick", {}, run_at=(datetime.utcnow() + timedelta(seconds=15)))
