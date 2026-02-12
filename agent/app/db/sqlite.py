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
from datetime import datetime

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
