from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timedelta

DATABASE_URL = "sqlite:///salestroopz.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# ----------------------------
# Workspace
# ----------------------------
class Workspace(Base):
    __tablename__ = "workspace"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    offering = Column(String)
    icp = Column(String)

    campaigns = relationship("Campaign", back_populates="workspace")


# ----------------------------
# Campaign
# ----------------------------
class Campaign(Base):
    __tablename__ = "campaign"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, ForeignKey("workspace.id"))
    name = Column(String)

    status = Column(String, default="draft")  
    # draft | running | paused | completed

    cadence_days = Column(Integer, default=3)
    max_touches = Column(Integer, default=4)
    sequence_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="campaigns")
    leads = relationship("Lead", back_populates="campaign")


# ----------------------------
# Lead
# ----------------------------
class Lead(Base):
    __tablename__ = "lead"

    id = Column(Integer, primary_key=True, index=True)

    campaign_id = Column(Integer, ForeignKey("campaign.id"))

    full_name = Column(String)
    email = Column(String, index=True)
    company = Column(String)

    state = Column(String, default="NEW")
    # NEW
    # WAITING_REPLY
    # FOLLOWUP
    # STOPPED_POSITIVE
    # STOPPED_NEGATIVE
    # COMPLETED

    touch_count = Column(Integer, default=0)

    next_touch_at = Column(DateTime, default=datetime.utcnow)

    conversation_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="leads")
    activities = relationship("ActivityLog", back_populates="lead")


# ----------------------------
# Activity Log
# ----------------------------
class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, ForeignKey("lead.id"))

    type = Column(String)
    # email_sent
    # reply_received
    # followup_scheduled
    # positive_detected
    # negative_detected

    message = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="activities")


# ----------------------------
# DB Helpers
# ----------------------------
def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()


# ----------------------------
# Workspace Save
# ----------------------------
def save_workspace(data):
    session = get_session()

    workspace = Workspace(
        company_name=data.company_name,
        offering=data.offering,
        icp=data.icp
    )

    session.add(workspace)
    session.commit()
    session.close()

# ----------------------------
# Workspace helpers
# ----------------------------
def get_latest_workspace():
    session = get_session()
    ws = session.query(Workspace).order_by(Workspace.id.desc()).first()
    session.close()
    return ws


# ----------------------------
# Campaign helpers
# ----------------------------
def create_campaign(workspace_id: int, name: str, cadence_days: int = 3, max_touches: int = 4):
    session = get_session()
    campaign = Campaign(
        workspace_id=workspace_id,
        name=name,
        status="draft",
        cadence_days=cadence_days,
        max_touches=max_touches,
    )
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    session.close()
    return campaign


def set_campaign_status(campaign_id: int, status: str):
    session = get_session()
    campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        session.close()
        return None
    campaign.status = status
    session.commit()
    session.refresh(campaign)
    session.close()
    return campaign


def get_campaign(campaign_id: int):
    session = get_session()
    campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
    session.close()
    return campaign


def list_campaigns(workspace_id: int):
    session = get_session()
    campaigns = (
        session.query(Campaign)
        .filter(Campaign.workspace_id == workspace_id)
        .order_by(Campaign.created_at.desc())
        .all()
    )
    session.close()
    return campaigns


# ----------------------------
# Lead helpers
# ----------------------------
def add_leads_bulk(campaign_id: int, leads: list[dict]):
    """
    leads items: {"full_name": "...", "email": "...", "company": "..."}
    """
    session = get_session()

    # (Optional) de-dupe within campaign by email
    existing = set(
        e[0] for e in session.query(Lead.email).filter(Lead.campaign_id == campaign_id).all()
        if e and e[0]
    )

    objs = []
    for l in leads:
        email = (l.get("email") or "").strip().lower()
        if not email or email in existing:
            continue
        existing.add(email)

        objs.append(
            Lead(
                campaign_id=campaign_id,
                full_name=(l.get("full_name") or "").strip(),
                email=email,
                company=(l.get("company") or "").strip(),
                state="NEW",
                touch_count=0,
                next_touch_at=datetime.utcnow(),
            )
        )

    session.add_all(objs)
    session.commit()
    count = len(objs)
    session.close()
    return count


def list_leads(campaign_id: int):
    session = get_session()
    leads = (
        session.query(Lead)
        .filter(Lead.campaign_id == campaign_id)
        .order_by(Lead.created_at.desc())
        .all()
    )
    session.close()
    return leads


def get_due_leads(campaign_id: int, limit: int = 10):
    session = get_session()
    now = datetime.utcnow()
    leads = (
        session.query(Lead)
        .filter(Lead.campaign_id == campaign_id)
        .filter(Lead.next_touch_at <= now)
        .filter(Lead.state.in_(["NEW", "FOLLOWUP"]))
        .order_by(Lead.next_touch_at.asc())
        .limit(limit)
        .all()
    )
    session.close()
    return leads


def mark_lead_waiting_reply(lead_id: int, cadence_days: int):
    session = get_session()
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        return None

    lead.touch_count = (lead.touch_count or 0) + 1
    lead.state = "WAITING_REPLY"
    lead.next_touch_at = datetime.utcnow() + timedelta(days=cadence_days)

    session.commit()
    session.refresh(lead)
    session.close()
    return lead


def schedule_followup(lead_id: int, days_from_now: int):
    session = get_session()
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        return None

    lead.state = "FOLLOWUP"
    lead.next_touch_at = datetime.utcnow() + timedelta(days=days_from_now)

    session.commit()
    session.refresh(lead)
    session.close()
    return lead


def stop_lead(lead_id: int, positive: bool, note: str = ""):
    session = get_session()
    lead = session.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        session.close()
        return None

    lead.state = "STOPPED_POSITIVE" if positive else "STOPPED_NEGATIVE"

    session.commit()
    session.refresh(lead)
    session.close()
    return lead


# ----------------------------
# Activity helpers
# ----------------------------
def log_activity(lead_id: int, type: str, message: str):
    session = get_session()
    row = ActivityLog(lead_id=lead_id, type=type, message=message)
    session.add(row)
    session.commit()
    session.refresh(row)
    session.close()
    return row


def get_campaign_activity(campaign_id: int, limit: int = 200):
    session = get_session()
    rows = (
        session.query(ActivityLog)
        .join(Lead, ActivityLog.lead_id == Lead.id)
        .filter(Lead.campaign_id == campaign_id)
        .order_by(ActivityLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    session.close()
    return rows
import json

def save_campaign_sequence(campaign_id: int, sequence: dict):
    session = get_session()
    campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        session.close()
        return None
    campaign.sequence_json = json.dumps(sequence)
    session.commit()
    session.refresh(campaign)
    session.close()
    return campaign

