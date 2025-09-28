from sqlalchemy import Column, Integer, String, DateTime, Boolean
from core.database_manager import Base
import datetime


class Alarm(Base):
    __tablename__ = "alarms"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    active = Column(Boolean, nullable=False, default=False)
    acknowledged = Column(Boolean, nullable=False, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message = Column(String(500))
    alarm_type = Column(String(100))
    device_id = Column(String(255))
    priority = Column(Integer, default=0)  # 0=niedrig, 1=mittel, 2=hoch, 3=kritisch

    @classmethod
    def from_dict(cls, data: dict):
        if "timestamp" in data and isinstance(data["timestamp"], str):
            import datetime
            data["timestamp"] = datetime.datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def to_json(self):
        return {
            "id": self.id,
            "active": self.active,
            "acknowledged": self.acknowledged,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "alarm_type": self.alarm_type,
            "device_id": self.device_id,
            "priority": self.priority
        }
