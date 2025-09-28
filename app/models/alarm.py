from sqlalchemy import Column, Integer, String, DateTime, Enum
from core.database_manager import Base
import datetime
import enum


class AlarmStatus(enum.Enum):
    AN = "an"
    AUS = "aus"
    QUITTIERT = "quittiert"


class Alarm(Base):
    __tablename__ = "alarms"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(Enum(AlarmStatus), nullable=False, default=AlarmStatus.AUS)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message = Column(String(500))
    alarm_type = Column(String(100))
    device_id = Column(String(255))
    priority = Column(Integer, default=0)  # 0=niedrig, 1=mittel, 2=hoch, 3=kritisch

    def to_json(self):
        return {
            "id": self.id,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "alarm_type": self.alarm_type,
            "device_id": self.device_id,
            "priority": self.priority
        }