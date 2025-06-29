"""
FastAPI main application entry point for Assistant Manager.
Implements agentic workflow architecture with LangGraph orchestration.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.dependencies import set_assistant_agent, set_scheduler_service, set_connection_manager
from app.api import agents, kanban, emails, reports
from app.services.scheduler_service import SchedulerService
from app.agents.assistant_agent import AssistantAgent
from app.models.database import initialize_database

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    
    logger.info("Starting Assistant Manager backend...")
    
    # Initialize database
    await initialize_database()
    
    # Initialize agent
    assistant_agent = AssistantAgent()
    await assistant_agent.initialize()
    set_assistant_agent(assistant_agent)
    
    # Initialize scheduler
    scheduler_service = SchedulerService(assistant_agent)
    await scheduler_service.start()
    set_scheduler_service(scheduler_service)
    
    logger.info("Backend initialization complete")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Assistant Manager backend...")
    from app.core.dependencies import get_scheduler_service, get_assistant_agent
    scheduler_service = get_scheduler_service()
    assistant_agent = get_assistant_agent()
    
    if scheduler_service:
        await scheduler_service.stop()
    if assistant_agent:
        await assistant_agent.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Assistant Manager API",
    description="Agentic workflow automation for team management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(kanban.router, prefix="/api/kanban", tags=["kanban"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()
set_connection_manager(manager)

@app.websocket("/ws/agent-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agent updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back for now - in production, this could handle client commands
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    """Health check endpoint."""
    from app.core.dependencies import get_assistant_agent
    assistant_agent = get_assistant_agent()
    return {
        "message": "Assistant Manager API is running",
        "version": "1.0.0",
        "agent_status": "active" if assistant_agent and assistant_agent.is_active else "inactive"
    }

@app.get("/health")
async def health_check():
    """Detailed health check."""
    from app.core.dependencies import get_assistant_agent, get_scheduler_service
    assistant_agent = get_assistant_agent()
    scheduler_service = get_scheduler_service()
    return {
        "status": "healthy",
        "agent_initialized": assistant_agent is not None,
        "scheduler_running": scheduler_service is not None and scheduler_service.is_running,
        "database": "connected"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )