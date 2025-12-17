"""FastAPI application entry point for the chatbot backend."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import UUID

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src import __version__
from src.api.models import (
    DependenciesHealth,
    DependencyStatus,
    DependencyStatusEnum,
    ErrorDetail,
    ErrorResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    JobStatusResponse,
    QueryRequest,
    QueryResponse,
    ReindexJobResponse,
    ReindexRequest,
    ServiceStatus,
    SessionDetails,
    SessionResponse,
)
from src.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events."""
    # Startup: Initialize connections
    settings = get_settings()
    app.state.settings = settings
    # TODO: Initialize Qdrant client
    # TODO: Initialize database connection pool
    # TODO: Initialize OpenAI client
    yield
    # Shutdown: Close connections
    # TODO: Close Qdrant client
    # TODO: Close database pool


app = FastAPI(
    title="Physical AI Book RAG Chatbot API",
    description="API for the RAG-powered chatbot embedded in the Physical AI & Humanoid Robotics book.",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom exception handler for consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                code=exc.detail if isinstance(exc.detail, str) else "ERROR",
                message=str(exc.detail),
            )
        ).model_dump(by_alias=True),
    )


# Health endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Service health check endpoint."""
    # TODO: Implement actual dependency checks
    return HealthResponse(
        status=ServiceStatus.HEALTHY,
        version=__version__,
        timestamp=datetime.now(timezone.utc),
        dependencies=DependenciesHealth(
            qdrant=DependencyStatus(status=DependencyStatusEnum.UP, latency_ms=10),
            postgres=DependencyStatus(status=DependencyStatusEnum.UP, latency_ms=5),
            openai=DependencyStatus(status=DependencyStatusEnum.UP, latency_ms=100),
        ),
    )


@app.get("/health/ready", tags=["Health"], status_code=status.HTTP_200_OK)
async def readiness_check() -> dict:
    """Readiness probe for container orchestration."""
    # TODO: Implement actual readiness checks
    return {"ready": True}


# Chat endpoints
@app.post(
    "/v1/chat/query",
    response_model=QueryResponse,
    tags=["Chat"],
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def submit_query(request: QueryRequest) -> QueryResponse:
    """Submit a question to the chatbot."""
    # TODO: Implement RAG pipeline
    # 1. Embed the query
    # 2. Search Qdrant for relevant chunks
    # 3. Build context from chunks
    # 4. Generate response with OpenAI
    # 5. Return response with citations
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Query endpoint not yet implemented",
    )


@app.post(
    "/v1/chat/feedback",
    response_model=FeedbackResponse,
    tags=["Chat"],
    responses={400: {"model": ErrorResponse}},
)
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Submit feedback on a chatbot response."""
    # TODO: Store feedback in database
    return FeedbackResponse(success=True, message="Feedback recorded. Thank you!")


# Session endpoints
@app.post(
    "/v1/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Sessions"],
)
async def create_session() -> SessionResponse:
    """Create a new chat session."""
    # TODO: Implement session creation in database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session creation not yet implemented",
    )


@app.get(
    "/v1/sessions/{session_id}",
    response_model=SessionDetails,
    tags=["Sessions"],
    responses={404: {"model": ErrorResponse}},
)
async def get_session(session_id: UUID) -> SessionDetails:
    """Get session details including conversation history."""
    # TODO: Fetch session from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="SESSION_NOT_FOUND",
    )


@app.delete(
    "/v1/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Sessions"],
    responses={404: {"model": ErrorResponse}},
)
async def delete_session(session_id: UUID) -> None:
    """End a chat session and clear associated data."""
    # TODO: Delete session from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="SESSION_NOT_FOUND",
    )


# Admin endpoints
def verify_admin_key(x_api_key: str = Header(...)) -> str:
    """Verify admin API key."""
    settings = get_settings()
    if not settings.admin_api_key or x_api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_API_KEY",
        )
    return x_api_key


@app.post(
    "/v1/admin/reindex",
    response_model=ReindexJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Admin"],
    responses={401: {"model": ErrorResponse}},
)
async def trigger_reindex(
    request: ReindexRequest = None,
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> ReindexJobResponse:
    """Trigger content reindexing job."""
    verify_admin_key(x_api_key)
    # TODO: Start background reindex job
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Reindex not yet implemented",
    )


@app.get(
    "/v1/admin/jobs/{job_id}",
    response_model=JobStatusResponse,
    tags=["Admin"],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_job_status(
    job_id: UUID,
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> JobStatusResponse:
    """Get status of a reindexing job."""
    verify_admin_key(x_api_key)
    # TODO: Fetch job status from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="JOB_NOT_FOUND",
    )
