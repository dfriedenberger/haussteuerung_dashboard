from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from core.database_manager import Base
import datetime


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message = Column(String)
    protocol = Column(String)
    level = Column(String)
    ref_id = Column(String, nullable=True)

    @classmethod
    def from_dict(cls, data: dict):
        if "timestamp" in data and isinstance(data["timestamp"], str):
            import datetime
            data["timestamp"] = datetime.datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def to_json(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "message": self.message,
            "protocol": self.protocol,
            "level": self.level,
            "ref_id": self.ref_id
        }
