from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///salestroopz.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Workspace(Base):
    __tablename__ = "workspace"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    offering = Column(String)
    icp = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_workspace(data):
    session = SessionLocal()
    workspace = Workspace(
        company_name=data.company_name,
        offering=data.offering,
        icp=data.icp
    )
    session.add(workspace)
    session.commit()
    session.close()
