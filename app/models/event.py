from sqlalchemy import Column, Integer, String, DateTime, JSON
from core.database_manager import Base
import datetime


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    payload = Column(JSON)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
