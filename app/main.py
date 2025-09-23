import asyncio
import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from fastapi.templating import Jinja2Templates

from api.protocol import Protocol
from core.database_manager import DatabaseManager
from api.dashboard import Dashboard
from core.event_manager import EventManager
from core.websocket_manager import WebSocketManager
from core.cycle_manager import CycleManager
from plugins.plugin_manager import PluginManager


def setup_logging(level=logging.INFO):
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
    )

    # uvicorn/error → umleiten
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn").handlers = []

    # Root-Logger konfigurieren (alle benutzen ihn dann)
    logger = logging.getLogger()
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).propagate = True

    return logger


logger = setup_logging(logging.INFO)

templates: Jinja2Templates = Jinja2Templates(directory="templates")


database_manager = DatabaseManager()

websocket_manager = WebSocketManager()

event_queue: asyncio.Queue = asyncio.Queue()

dashboard = Dashboard(websocket_manager, database_manager, templates)

protocol = Protocol(websocket_manager, database_manager, templates)

plugin_manager = PluginManager(event_queue)
plugin_manager.load()


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Start cycle manager & event manager task ...")
    stop_event = asyncio.Event()
    cycle_manager = CycleManager(stop_event, event_queue, interval=60)
    event_manager = EventManager(stop_event, event_queue, websocket_manager, database_manager, plugin_manager)
    cycle_task = asyncio.create_task(cycle_manager.run())
    event_task = asyncio.create_task(event_manager.run())

    logger.info("Tasks started")
    try:
        yield
    finally:
        logger.info("Stopping tasks...")
        stop_event.set()
        await cycle_task
        await event_task
        logger.info("Tasks stopped")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        print("Noch laufende Tasks:", tasks)


app = FastAPI(title="Haussteuerung Dashboard", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(dashboard.router)
app.include_router(protocol.router)


@app.get("/")
async def redirect():
    # redirect to /dashboard
    return RedirectResponse(url="/dashboard")
