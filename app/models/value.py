from sqlalchemy import Column, String, DateTime, JSON
import datetime
from core.database_manager import Base


class Value(Base):
    __tablename__ = "values"
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, primary_key=True, default=datetime.datetime.utcnow)
    value_type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    unit = Column(String, nullable=True)

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
            "value_type": self.value_type,
            "value": self.value,
            "unit": self.unit
        }
