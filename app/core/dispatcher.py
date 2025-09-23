import threading
import queue
import logging
import time
from datetime import datetime

from core.websocket_manager import WebSocketManager
from core.database import DatabaseManager
from services.value_service import ValueService
from .event_type import EventType
#from plugins.plugin_loader import load_plugins

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, websocket_manager: WebSocketManager):
        self.is_running = False
        self._threads = []
        self._plugins = []
        self.queue = queue.Queue()
        self.websocket_manager = websocket_manager

    def start(self):
        """Start the background threads"""
        if self.is_running:
            logger.warning("Dispatcher is already running")
            return

        self.is_running = True
        logger.info("Starting dispatcher...")

        # Loading all plugins (lazy import to avoid circular dependency)
        self._plugins = []  # load_plugins()
        for plugin in self._plugins:
            plugin.set_dispatcher(self)

        # Trigger start event
        self.queue.put((EventType.START, {}))

        # Start threads
        cycle_thread = threading.Thread(target=self._cycle, name="dispatcher-cycle", daemon=True)
        event_thread = threading.Thread(target=self._events, name="dispatcher-events", daemon=True)

        cycle_thread.start()
        event_thread.start()

        self._threads = [cycle_thread, event_thread]

        logger.info("Dispatcher started successfully")

    def stop(self):
        """Stop the dispatcher threads"""
        if not self.is_running:
            return

        self.is_running = False
        logger.info("Stopping dispatcher...")

        # Trigger stop event
        self.queue.put((EventType.STOP, {}), timeout=1)

        # Todo wait until queue is empty, all plugins ready

        # Wait for threads to complete
        for thread in self._threads:
            logger.info(f"Waiting for thread {thread.name} to stop")
            thread.join()
            logger.info(f"Thread {thread.name} has stopped")

        self._threads = []
        logger.info("Dispatcher stopped")

    def _cycle(self):
        """creates cyclic events every 60 seconds"""
        try:
            counter = 0
            while self.is_running:

                if counter % 60 == 0:
                    # Trigger cycle event
                    payload = {
                        "type": "60_seconds",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    self.queue.put((EventType.CYCLE, payload), timeout=1)
                   
                time.sleep(1)
                counter += 1

        except Exception as e:
            logger.error(f"Cycle thread failed: {e}")
        finally:
            logger.info("Cycle thread stopped")

    def _events(self):
        """handles events"""
        try:
            while self.is_running:
                try:
                    # Get event with timeout to allow for shutdown
                    event_type, payload = self.queue.get(timeout=1)

                    logger.info(f"Handling event: {event_type} with payload: {payload}")

                    # Handle special events
                    #if event_type == EventType.STOP:
                    #    logger.info("Received stop event")
                    #    break

                    #if event_type == EventType.LOG:
                    #    self._handle_log_event(payload)

                    #if event_type == EventType.VALUE:
                    #    self._handle_value_event(payload)

                    # Trigger plugins in separate thread to avoid blocking
                    #self._trigger_plugins_async(event_type, payload)

                    #self.queue.task_done()

                except queue.Empty:
                    # Timeout - continue loop to check shutdown
                    continue

        except Exception as e:
            logger.error(f"Event handler thread failed: {e}")
        finally:
            logger.info("Event handler thread stopped")

    def _trigger_plugins_async(self, event_type: EventType, payload: dict):
        """Trigger plugins in a separate thread to avoid blocking"""
        def trigger_plugins():
            for plugin in self._plugins:
                try:
                    plugin.trigger(event_type, payload)
                except Exception as e:
                    logger.error(f"Error in plugin {plugin.__class__.__name__} during event {event_type}: {e}")
        
        # Start plugin execution in separate thread
        plugin_thread = threading.Thread(
            target=trigger_plugins,
            name=f"plugin-trigger-{event_type.name}",
            daemon=True
        )
        plugin_thread.start()

    def _handle_log_event(self, payload: dict):
        """Handle log event by broadcasting to WebSocket manager"""
        # Note: WebSocket manager calls need to be made async-safe
        # For now, we'll skip the WebSocket broadcast from this thread
        pass

    def _handle_value_event(self, payload: dict):
        """Handle value event by broadcasting to WebSocket manager"""
        # Note: WebSocket manager calls need to be made async-safe
        # For now, we'll skip the WebSocket broadcast from this thread
        pass

    def put_event(self, event_type: EventType, payload: dict):
        """Thread-safe method to put events into the queue"""
        try:
            self.queue.put((event_type, payload), timeout=1)
        except queue.Full:
            logger.warning(f"Could not queue event {event_type} - queue full")



