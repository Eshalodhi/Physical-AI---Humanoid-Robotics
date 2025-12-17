"""Pydantic models for the chatbot API.

Models defined according to contracts/chatbot-api.yaml OpenAPI specification.
"""

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Enums
class QueryScope(str, Enum):
    """Scope of the search query."""

    FULL = "full"
    SELECTED = "selected"


class FeedbackRating(str, Enum):
    """Rating for response feedback."""

    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


class ServiceStatus(str, Enum):
    """Overall service health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyStatusEnum(str, Enum):
    """Individual dependency status."""

    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"


class JobStatus(str, Enum):
    """Background job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Request Models
class QueryRequest(BaseModel):
    """Request body for /chat/query endpoint."""

    query: str = Field(..., min_length=1, max_length=1000, description="The user's question")
    scope: QueryScope = Field(default=QueryScope.FULL, description="Search scope")
    selected_text: Optional[str] = Field(
        default=None,
        max_length=2000,
        alias="selectedText",
        description="Text selected by user (required when scope is 'selected')",
    )
    current_page: Optional[str] = Field(
        default=None, alias="currentPage", description="Current page path for context"
    )
    session_id: Optional[UUID] = Field(
        default=None, alias="sessionId", description="Session ID for conversation continuity"
    )

    model_config = {"populate_by_name": True}


class FeedbackRequest(BaseModel):
    """Request body for /chat/feedback endpoint."""

    response_id: UUID = Field(..., alias="responseId", description="ID of the response being rated")
    rating: FeedbackRating
    comment: Optional[str] = Field(
        default=None, max_length=500, description="Optional feedback comment"
    )

    model_config = {"populate_by_name": True}


class ReindexRequest(BaseModel):
    """Request body for /admin/reindex endpoint."""

    chapters: Optional[List[str]] = Field(
        default=None, description="Specific chapter IDs to reindex. Empty for full reindex."
    )


# Response Models
class Citation(BaseModel):
    """A citation reference to source material."""

    chapter_title: str = Field(..., alias="chapterTitle")
    chapter_slug: str = Field(..., alias="chapterSlug")
    section_title: Optional[str] = Field(default=None, alias="sectionTitle")
    relevance_score: float = Field(..., ge=0, le=1, alias="relevanceScore")
    excerpt: Optional[str] = Field(default=None, max_length=200)

    model_config = {"populate_by_name": True}


class TokenUsage(BaseModel):
    """Token usage statistics for a query."""

    prompt_tokens: int = Field(..., alias="promptTokens")
    completion_tokens: int = Field(..., alias="completionTokens")
    total_tokens: int = Field(..., alias="totalTokens")

    model_config = {"populate_by_name": True}


class QueryResponse(BaseModel):
    """Response body for /chat/query endpoint."""

    id: UUID
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    is_out_of_scope: bool = Field(default=False, alias="isOutOfScope")
    confidence: float = Field(..., ge=0, le=1)
    usage: Optional[TokenUsage] = None
    latency_ms: int = Field(..., alias="latencyMs")

    model_config = {"populate_by_name": True}


class FeedbackResponse(BaseModel):
    """Response body for /chat/feedback endpoint."""

    success: bool
    message: str


class SessionResponse(BaseModel):
    """Response body for POST /sessions endpoint."""

    session_id: UUID = Field(..., alias="sessionId")
    created_at: datetime = Field(..., alias="createdAt")
    expires_at: datetime = Field(..., alias="expiresAt")

    model_config = {"populate_by_name": True}


class ConversationEntry(BaseModel):
    """A single entry in conversation history."""

    query: str
    answer: str
    timestamp: datetime


class SessionDetails(BaseModel):
    """Response body for GET /sessions/{sessionId} endpoint."""

    session_id: UUID = Field(..., alias="sessionId")
    created_at: datetime = Field(..., alias="createdAt")
    last_activity_at: datetime = Field(..., alias="lastActivityAt")
    expires_at: datetime = Field(..., alias="expiresAt")
    query_count: int = Field(..., alias="queryCount")
    conversation_history: List[ConversationEntry] = Field(
        default_factory=list, alias="conversationHistory"
    )

    model_config = {"populate_by_name": True}


class DependencyStatus(BaseModel):
    """Health status of a single dependency."""

    status: DependencyStatusEnum
    latency_ms: Optional[int] = Field(default=None, alias="latencyMs")
    message: Optional[str] = None

    model_config = {"populate_by_name": True}


class DependenciesHealth(BaseModel):
    """Health status of all dependencies."""

    qdrant: DependencyStatus
    postgres: DependencyStatus
    openai: DependencyStatus


class HealthResponse(BaseModel):
    """Response body for /health endpoint."""

    status: ServiceStatus
    version: str
    timestamp: datetime
    dependencies: DependenciesHealth


class ReindexJobResponse(BaseModel):
    """Response body for POST /admin/reindex endpoint."""

    job_id: UUID = Field(..., alias="jobId")
    status: JobStatus
    started_at: datetime = Field(..., alias="startedAt")
    estimated_chunks: Optional[int] = Field(default=None, alias="estimatedChunks")

    model_config = {"populate_by_name": True}


class JobProgress(BaseModel):
    """Progress information for a background job."""

    chunks_processed: int = Field(..., alias="chunksProcessed")
    chunks_total: int = Field(..., alias="chunksTotal")
    percent_complete: float = Field(..., alias="percentComplete")

    model_config = {"populate_by_name": True}


class JobStatusResponse(BaseModel):
    """Response body for GET /admin/jobs/{jobId} endpoint."""

    job_id: UUID = Field(..., alias="jobId")
    status: JobStatus
    started_at: datetime = Field(..., alias="startedAt")
    completed_at: Optional[datetime] = Field(default=None, alias="completedAt")
    progress: Optional[JobProgress] = None
    errors: List[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str
    message: str
    details: Optional[dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    error: ErrorDetail
