from sqlalchemy.orm import Session
from sqlalchemy import func
from models.value import Value


# values
def get_current_values(db: Session):
    """
    Internal function to get current values (used by both REST and WebSocket)
    """
    # Subquery to get the latest timestamp for each device ID
    latest_timestamps = db.query(
        Value.id,
        func.max(Value.timestamp).label('latest_timestamp')
    ).group_by(Value.id).subquery()

    # Join to get the actual values with the latest timestamps
    return db.query(Value).join(
        latest_timestamps,
        (Value.id == latest_timestamps.c.id) &
        (Value.timestamp == latest_timestamps.c.latest_timestamp)
    ).all()
