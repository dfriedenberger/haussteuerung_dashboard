from sqlalchemy.orm import Session
from models.log import Log
from models.value import Value
from core.event_manager import event_manager
from app.core.database_manager import get_db
import datetime
import logging

logger = logging.getLogger(__name__)


class DeviceService:
    def __init__(self):
        pass

    def get_devices(self):
        return []

    def control_device(self, device_id, command):
        return {"status": "ok"}
    
    async def create_log_entry(self, message: str, protocol: str, level: str, ref_id: str = None, db: Session = None):
        """Create a new log entry and trigger WebSocket broadcast"""
        if db is None:
            # If no DB session provided, create a new one
            db_gen = get_db()
            db = next(db_gen)
            close_db = True
        else:
            close_db = False
        
        try:
            # Create new log entry
            log_entry = Log(
                message=message,
                protocol=protocol,
                level=level,
                ref_id=ref_id,
                timestamp=datetime.datetime.utcnow()
            )
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            
            # Prepare data for event system
            log_data = {
                "id": log_entry.id,
                "timestamp": log_entry.timestamp.isoformat(),
                "message": log_entry.message,
                "protocol": log_entry.protocol,
                "level": log_entry.level,
                "ref_id": log_entry.ref_id
            }
            
            # Trigger event with WebSocket broadcast
            await event_manager.trigger_log_event(log_data)
            
            logger.info(f"Created log entry: {message} (ID: {log_entry.id})")
            return log_entry
            
        except Exception as e:
            logger.error(f"Error creating log entry: {e}")
            db.rollback()
            raise
        finally:
            if close_db:
                db.close()
    
    async def create_value_entry(self, device_id: str, value_type: str, value: any, unit: str = "", db: Session = None):
        """Create a new value entry and trigger WebSocket broadcast"""
        if db is None:
            # If no DB session provided, create a new one
            db_gen = get_db()
            db = next(db_gen)
            close_db = True
        else:
            close_db = False
        
        try:
            # Create new value entry
            value_entry = Value(
                id=device_id,
                timestamp=datetime.datetime.utcnow(),
                value={
                    "type": value_type,
                    "value": value,
                    "unit": unit
                }
            )
            
            db.add(value_entry)
            db.commit()
            db.refresh(value_entry)
            
            # Get updated dashboard data for broadcast
            from api.dashboard import _get_current_values
            values_data = await _get_current_values(db)
            
            # Trigger event with WebSocket broadcast
            await event_manager.trigger_value_event(values_data)
            
            logger.info(f"Created value entry for {device_id}: {value_type}={value}{unit}")
            return value_entry
            
        except Exception as e:
            logger.error(f"Error creating value entry: {e}")
            db.rollback()
            raise
        finally:
            if close_db:
                db.close()


# Global instance
device_service = DeviceService()
