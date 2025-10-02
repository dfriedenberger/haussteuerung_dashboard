import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models.value import Value
from models.alarm import Alarm
from models.log import Log

logger = logging.getLogger(__name__)


# Logs
def create_log(db: Session, new_log: Log):
    """
    Create a new log entry.
    """
    db.add(new_log)
    db.commit()


# Values
def create_or_update_value(db: Session, new_value: Value):
    """
    Create a new value or update an existing one based on id and timestamp.
    """
    existing_value = db.query(Value).filter_by(id=new_value.id, timestamp=new_value.timestamp).one_or_none()

    if existing_value:
        logger.warning(f"Value with id {new_value.id} and timestamp {new_value.timestamp} already exists. Skip insert")
    else:
        db.add(new_value)
        db.commit()


def read_value_or_null(db: Session, value_id: str):
    """
    Read the latest value for a given device ID, or return None if not found.
    """
    return db.query(Value).filter_by(id=value_id).order_by(desc(Value.timestamp)).first()


def read_current_values(db: Session):
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


# Alarms
def create_or_update_alarm(db: Session, new_alarm):
    """
    Create a new alarm or update an existing one based on device_id and alarm_type.
    """
    existing_alarm = db.query(Alarm).filter_by(
        device_id=new_alarm.device_id,
        alarm_type=new_alarm.alarm_type
    ).one_or_none()

    if existing_alarm:
        # Update existing alarm
        existing_alarm.active = new_alarm.active
        existing_alarm.acknowledged = new_alarm.acknowledged
        existing_alarm.timestamp = new_alarm.timestamp
        existing_alarm.message = new_alarm.message
        existing_alarm.priority = new_alarm.priority
        db.add(existing_alarm)
    else:
        # Create new alarm
        db.add(new_alarm)
    db.commit()


def update_alarm_acknowledged(db: Session, alarm_id: int):
    """Update the acknowledged status of an alarm."""
    alarm = db.query(Alarm).filter_by(id=alarm_id).first()
    if alarm:
        alarm.acknowledged = True
        db.add(alarm)
        db.commit()
    else:
        logger.warning(f"Alarm with ID {alarm_id} not found")


def read_alarms(db: Session):
    """
    Read all alarms from the database.
    """
    return db.query(Alarm).order_by(desc(Alarm.priority), desc(Alarm.timestamp)).all()
