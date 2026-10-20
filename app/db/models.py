from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MuleEntity(Base):
    __tablename__ = "mule_entities"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True) # "account" or "phone"
    value_hash = Column(String, unique=True, index=True)
    value_masked = Column(String)
    source = Column(String)
    report_count = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

class UserReport(Base):
    __tablename__ = "user_reports"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String)
    value_hash = Column(String, index=True)
    scam_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    reporter_hash = Column(String)

class CheckLog(Base):
    __tablename__ = "check_logs"
    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String) # "web" or "whatsapp"
    input_type = Column(String) # "text" or "image"
    verdict = Column(String)
    score = Column(Float)
    latency_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScamPattern(Base):
    __tablename__ = "scam_patterns"
    id = Column(Integer, primary_key=True, index=True)
    scam_type = Column(String)
    keyword = Column(String)
    language = Column(String)
    weight = Column(Integer)