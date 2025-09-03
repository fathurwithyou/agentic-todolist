"""
FastAPI Timeline to Calendar Application
Clean architecture with proper separation of concerns.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.utils.logging import setup_logging
from app.config.settings import get_config
from app.api.v1 import health  # Keep health check from v1
from app.api import auth, calendar, api_keys, timeline, tasks


# Set up logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    print("Starting FastAPI application...")

    # Calendar service initialization moved to per-request basis
    print("Calendar service will be initialized per user request")

    yield

    # Shutdown
    print("Shutting down FastAPI application...")


# Initialize FastAPI app
app = FastAPI(
    title="Timeline to Calendar API",
    description="FastAPI backend service for creating Google Calendar events from timeline text using configurable AI models",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health.router)  # Health check from v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(
    auth.router
)  # Also include auth routes at root level for backward compatibility
app.include_router(api_keys.router, prefix="/api/v1")
app.include_router(
    calendar.router, prefix="/api/v1"
)  # Calendar API (/api/v1/calendar/*)
app.include_router(
    timeline.router, prefix="/api/v1"
)  # Timeline API (/api/v1/timeline/*)
app.include_router(
    tasks.router, prefix="/api/v1"
)  # Tasks API (/api/v1/tasks/*)

# Serve static frontend files
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")


@app.get("/api")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Timeline to Calendar API",
        "version": "1.0.0",
        "endpoints": {
            "GET /auth/google": "Initiate Google OAuth login",
            "GET /auth/google/callback": "Handle Google OAuth callback",
            "GET /auth/verify": "Verify JWT token",
            "GET /auth/profile": "Get user profile",
            "GET /auth/calendar-status": "Check Google Calendar access status",
            "POST /auth/logout": "Logout user",
            "POST /api/v1/api-keys/save": "Save API key securely",
            "GET /api/v1/api-keys/list": "List saved API keys",
            "GET /api/v1/api-keys/test/{provider}": "Test API key validity",
            "DELETE /api/v1/api-keys/remove/{provider}": "Remove API key",
            "GET /api/v1/api-keys/providers": "Get available LLM providers",
            "GET /api/v1/api-keys/list/{user_id}": "List API keys (backward compatibility)",
            "GET /api/v1/api-keys/test/{user_id}/{provider}": "Test API key (backward compatibility)",
            "GET /api/v1/timeline/providers": "Get available timeline providers",
            "POST /api/v1/timeline/preview": "Preview timeline parsing",
            "POST /api/v1/timeline/create-events": "Create events from timeline preview",
            "GET /api/v1/calendar/google/calendars": "List user's Google Calendars",
            "GET /api/v1/calendar/google/calendars/writable": "List user's writable Google Calendars",
            "GET /api/v1/calendar/google/events": "List user's Google Calendar events",
            "POST /api/v1/calendar/google/events": "Create event in Google Calendar",
            "PUT /api/v1/calendar/google/events/{event_id}": "Update Google Calendar event",
            "DELETE /api/v1/calendar/google/events/{event_id}": "Delete Google Calendar event",
            "GET /api/v1/tasks/lists": "List task lists",
            "POST /api/v1/tasks/lists": "Create task list",
            "GET /api/v1/tasks/{list_id}": "List tasks in a list",
            "POST /api/v1/tasks/{list_id}/tasks": "Create task",
            "PATCH /api/v1/tasks/{list_id}/tasks/{task_id}": "Update task",
            "DELETE /api/v1/tasks/{list_id}/tasks/{task_id}": "Delete task",
            "POST /api/v1/tasks/{list_id}/parse": "Parse timeline text into tasks",
            "POST /api/v1/tasks/{list_id}/sync": "Sync tasks with Google Tasks",
            "GET /health": "Health check",
            "GET /docs": "API documentation",
        },
    }


def main():
    """Run the FastAPI application"""
    config = get_config()

    # Validate configuration before starting (skip for demo)
    if not config.validate_config():
        print("Configuration validation failed. Running in demo mode...")
        print(
            "Note: Google Calendar features will not work without proper credentials."
        )

    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
