"""
Data models for OpenPolicy Scraper Service

This module defines all data models used throughout the scraper service,
including Pydantic models for API requests/responses and internal data structures.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid

# ============================================================================
# ENUMS
# ============================================================================

class ScraperStatus(str, Enum):
    """Scraper execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"
    SCHEDULED = "scheduled"

class ScraperPriority(str, Enum):
    """Scraper priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class DataType(str, Enum):
    """Types of data collected"""
    BILLS = "bills"
    REPRESENTATIVES = "representatives"
    VOTES = "votes"
    COMMITTEES = "committees"
    SESSIONS = "sessions"
    DEBATES = "debates"
    POLITICIANS = "politicians"
    PARTIES = "parties"
    DISTRICTS = "districts"
    JURISDICTIONS = "jurisdictions"

class JurisdictionLevel(str, Enum):
    """Jurisdiction levels"""
    FEDERAL = "federal"
    PROVINCIAL = "provincial"
    MUNICIPAL = "municipal"

# ============================================================================
# BASE MODELS
# ============================================================================

class BaseScraperModel(BaseModel):
    """Base model for all scraper-related models"""
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }

# ============================================================================
# SCRAPER MODELS
# ============================================================================

class ScraperInfo(BaseScraperModel):
    """Scraper information model"""
    name: str = Field(..., description="Unique scraper name")
    enabled: bool = Field(default=True, description="Whether scraper is enabled")
    schedule: str = Field(default="daily", description="Execution schedule")
    priority: ScraperPriority = Field(default=ScraperPriority.MEDIUM, description="Scraper priority")
    jurisdiction_level: JurisdictionLevel = Field(..., description="Jurisdiction level")
    source_url: str = Field(..., description="Data source URL")
    description: str = Field(default="", description="Scraper description")
    version: str = Field(default="1.0.0", description="Scraper version")
    last_run: Optional[datetime] = Field(default=None, description="Last execution time")
    next_run: Optional[datetime] = Field(default=None, description="Next scheduled execution")
    status: ScraperStatus = Field(default=ScraperStatus.IDLE, description="Current status")
    data_collected: int = Field(default=0, description="Total data collected")
    success_rate: float = Field(default=0.0, description="Success rate percentage")
    avg_duration: float = Field(default=0.0, description="Average execution duration")
    error_count: int = Field(default=0, description="Total error count")
    last_error: Optional[str] = Field(default=None, description="Last error message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class ScraperRunRequest(BaseScraperModel):
    """Request model for running a scraper"""
    scraper_name: str = Field(..., description="Name of scraper to run")
    force: bool = Field(default=False, description="Force execution even if disabled")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")
    priority: ScraperPriority = Field(default=ScraperPriority.MEDIUM, description="Execution priority")
    timeout: int = Field(default=3600, description="Execution timeout in seconds")

class ScraperRunResponse(BaseScraperModel):
    """Response model for scraper execution"""
    scraper_name: str = Field(..., description="Name of executed scraper")
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Job status")
    message: str = Field(..., description="Response message")
    estimated_duration: Optional[int] = Field(default=None, description="Estimated duration in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")

class ScraperConfiguration(BaseScraperModel):
    """Scraper configuration model"""
    scraper_name: str = Field(..., description="Scraper name")
    config: Dict[str, Any] = Field(..., description="Configuration parameters")
    environment: str = Field(default="development", description="Environment")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

# ============================================================================
# JOB MODELS
# ============================================================================

class ScraperJob(BaseScraperModel):
    """Scraper job model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique job identifier")
    scraper_name: str = Field(..., description="Associated scraper name")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Job status")
    priority: ScraperPriority = Field(default=ScraperPriority.MEDIUM, description="Job priority")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Job parameters")
    started_at: Optional[datetime] = Field(default=None, description="Job start time")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion time")
    duration: Optional[float] = Field(default=None, description="Execution duration in seconds")
    data_collected: int = Field(default=0, description="Amount of data collected")
    error_count: int = Field(default=0, description="Number of errors encountered")
    error_messages: List[str] = Field(default_factory=list, description="Error messages")
    progress: float = Field(default=0.0, description="Progress percentage (0-100)")
    result_summary: Optional[Dict[str, Any]] = Field(default=None, description="Job result summary")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class JobCreateRequest(BaseScraperModel):
    """Request model for creating a job"""
    scraper_name: str = Field(..., description="Scraper name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Job parameters")
    priority: ScraperPriority = Field(default=ScraperPriority.MEDIUM, description="Job priority")
    schedule_at: Optional[datetime] = Field(default=None, description="Scheduled execution time")

class JobUpdateRequest(BaseScraperModel):
    """Request model for updating a job"""
    status: Optional[JobStatus] = Field(default=None, description="New job status")
    priority: Optional[ScraperPriority] = Field(default=None, description="New job priority")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Updated parameters")

# ============================================================================
# DATA MODELS
# ============================================================================

class DataRecord(BaseScraperModel):
    """Data record model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique record identifier")
    scraper_name: str = Field(..., description="Source scraper name")
    data_type: DataType = Field(..., description="Type of data")
    jurisdiction_level: JurisdictionLevel = Field(..., description="Jurisdiction level")
    jurisdiction_name: str = Field(..., description="Jurisdiction name")
    raw_data: Dict[str, Any] = Field(..., description="Raw scraped data")
    processed_data: Optional[Dict[str, Any]] = Field(default=None, description="Processed data")
    validation_status: str = Field(default="pending", description="Data validation status")
    quality_score: Optional[float] = Field(default=None, description="Data quality score")
    collected_at: datetime = Field(default_factory=datetime.utcnow, description="Data collection timestamp")
    processed_at: Optional[datetime] = Field(default=None, description="Data processing timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")

class DataQueryRequest(BaseScraperModel):
    """Request model for querying data"""
    scraper_name: Optional[str] = Field(default=None, description="Filter by scraper name")
    data_type: Optional[DataType] = Field(default=None, description="Filter by data type")
    jurisdiction_level: Optional[JurisdictionLevel] = Field(default=None, description="Filter by jurisdiction level")
    jurisdiction_name: Optional[str] = Field(default=None, description="Filter by jurisdiction name")
    start_date: Optional[datetime] = Field(default=None, description="Start date filter")
    end_date: Optional[datetime] = Field(default=None, description="End date filter")
    limit: int = Field(default=100, description="Maximum number of records")
    offset: int = Field(default=0, description="Number of records to skip")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order (asc/desc)")

class DataExportRequest(BaseScraperModel):
    """Request model for exporting data"""
    scraper_name: Optional[str] = Field(default=None, description="Filter by scraper name")
    data_type: Optional[DataType] = Field(default=None, description="Filter by data type")
    jurisdiction_level: Optional[JurisdictionLevel] = Field(default=None, description="Filter by jurisdiction level")
    start_date: Optional[datetime] = Field(default=None, description="Start date filter")
    end_date: Optional[datetime] = Field(default=None, description="End date filter")
    format: str = Field(default="json", description="Export format (json, csv, xml)")
    include_raw: bool = Field(default=False, description="Include raw data in export")

# ============================================================================
# MONITORING MODELS
# ============================================================================

class HealthStatus(BaseScraperModel):
    """Health status model"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")
    services: Dict[str, str] = Field(..., description="Individual service statuses")
    dependencies: Dict[str, str] = Field(..., description="External dependency statuses")

class MetricsSummary(BaseScraperModel):
    """Metrics summary model"""
    total_scrapers: int = Field(..., description="Total number of scrapers")
    active_scrapers: int = Field(..., description="Number of active scrapers")
    total_jobs: int = Field(..., description="Total number of jobs")
    running_jobs: int = Field(..., description="Number of running jobs")
    total_data_collected: int = Field(..., description="Total data collected")
    success_rate: float = Field(..., description="Overall success rate")
    avg_response_time: float = Field(..., description="Average response time")
    error_rate: float = Field(..., description="Overall error rate")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")

class Alert(BaseScraperModel):
    """Alert model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique alert identifier")
    level: str = Field(..., description="Alert level (info, warning, error, critical)")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    scraper_name: Optional[str] = Field(default=None, description="Associated scraper")
    job_id: Optional[str] = Field(default=None, description="Associated job")
    acknowledged: bool = Field(default=False, description="Whether alert is acknowledged")
    acknowledged_at: Optional[datetime] = Field(default=None, description="Acknowledgment timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation timestamp")

# ============================================================================
# VALIDATION MODELS
# ============================================================================

class DataValidationResult(BaseScraperModel):
    """Data validation result model"""
    record_id: str = Field(..., description="Record identifier")
    validation_status: str = Field(..., description="Validation status")
    quality_score: float = Field(..., description="Quality score (0-100)")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    validation_warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")

# ============================================================================
# UTILITY MODELS
# ============================================================================

class PaginatedResponse(BaseScraperModel):
    """Generic paginated response model"""
    data: List[Any] = Field(..., description="Response data")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")

class ErrorResponse(BaseScraperModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request identifier")

class SuccessResponse(BaseScraperModel):
    """Success response model"""
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(default=None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
