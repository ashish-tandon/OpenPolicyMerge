"""
Data Source model for managing external data sources.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, Boolean, JSON, Float
from sqlalchemy.orm import relationship
import enum

from .base import Base


class SourceType(enum.Enum):
    """Data source type enumeration."""
    API = "api"
    DATABASE = "database"
    FILE = "file"
    WEB_SCRAPING = "web_scraping"
    STREAMING = "streaming"
    BATCH = "batch"


class SourceStatus(enum.Enum):
    """Data source status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    DEPRECATED = "deprecated"


class AuthenticationType(enum.Enum):
    """Authentication type enumeration."""
    NONE = "none"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    CUSTOM = "custom"


class DataSource(Base):
    """Data Source model for managing external data sources."""
    
    __tablename__ = "datasources"
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    source_type = Column(Enum(SourceType), nullable=False, index=True)
    status = Column(Enum(SourceStatus), default=SourceStatus.ACTIVE, index=True)
    
    # Connection details
    url = Column(String(500), nullable=True)
    host = Column(String(255), nullable=True)
    port = Column(Integer, nullable=True)
    database_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)  # Encrypted in production
    
    # Authentication
    auth_type = Column(Enum(AuthenticationType), default=AuthenticationType.NONE)
    auth_config = Column(JSON, nullable=True)  # Authentication configuration
    
    # Data specifications
    data_format = Column(String(100), nullable=True)  # JSON, CSV, XML, etc.
    encoding = Column(String(50), default="utf-8")
    delimiter = Column(String(10), nullable=True)  # For CSV files
    has_header = Column(Boolean, default=True)  # For file sources
    
    # Scheduling and frequency
    update_frequency = Column(String(100), nullable=True)  # Daily, hourly, etc.
    last_updated = Column(DateTime, nullable=True)
    next_update = Column(DateTime, nullable=True)
    
    # Performance metrics
    response_time = Column(Float, nullable=True)  # Average response time in seconds
    success_rate = Column(Float, default=100.0)  # Success rate percentage
    total_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Data quality
    record_count = Column(Integer, default=0)
    data_size = Column(Integer, default=0)  # Size in bytes
    last_record_count = Column(Integer, default=0)
    last_data_size = Column(Integer, default=0)
    
    # Configuration
    config = Column(JSON, nullable=True)  # Source-specific configuration
    headers = Column(JSON, nullable=True)  # HTTP headers for API sources
    parameters = Column(JSON, nullable=True)  # Query parameters
    timeout = Column(Integer, default=30)  # Request timeout in seconds
    retry_attempts = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)  # Delay between retries in seconds
    
    # Monitoring and alerts
    health_check_enabled = Column(Boolean, default=True)
    health_check_interval = Column(Integer, default=300)  # Health check interval in seconds
    last_health_check = Column(DateTime, nullable=True)
    health_check_status = Column(String(50), default="unknown")
    
    # Relationships
    etl_jobs = relationship("ETLJob", back_populates="data_source")
    quality_metrics = relationship("DataQualityMetric", back_populates="data_source")
    
    def __init__(self, **kwargs):
        """Initialize Data Source with UUID."""
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    @property
    def connection_string(self) -> Optional[str]:
        """Generate connection string based on source type."""
        if self.source_type == SourceType.DATABASE:
            if self.host and self.port and self.database_name:
                return f"{self.host}:{self.port}/{self.database_name}"
        elif self.source_type == SourceType.API:
            return self.url
        elif self.source_type == SourceType.FILE:
            return self.url
        return None
    
    @property
    def is_healthy(self) -> bool:
        """Check if data source is healthy."""
        if not self.health_check_enabled:
            return True
        
        if not self.last_health_check:
            return False
        
        # Check if health check is recent (within 2x interval)
        time_since_check = (datetime.utcnow() - self.last_health_check).total_seconds()
        return time_since_check <= (self.health_check_interval * 2)
    
    @property
    def is_due_for_update(self) -> bool:
        """Check if data source is due for update."""
        if not self.next_update:
            return False
        return datetime.utcnow() >= self.next_update
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    @property
    def data_growth_rate(self) -> float:
        """Calculate data growth rate."""
        if self.last_record_count == 0:
            return 0.0
        return ((self.record_count - self.last_record_count) / self.last_record_count) * 100
    
    def update_health_status(self, status: str, response_time: float = None) -> None:
        """Update health check status."""
        self.health_check_status = status
        self.last_health_check = datetime.utcnow()
        if response_time is not None:
            self.response_time = response_time
        self.updated_at = datetime.utcnow()
    
    def record_request(self, success: bool, response_time: float = None) -> None:
        """Record a request attempt."""
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
        
        if response_time is not None:
            # Update average response time
            if self.response_time is None:
                self.response_time = response_time
            else:
                self.response_time = (self.response_time + response_time) / 2
        
        # Update success rate
        self.success_rate = ((self.total_requests - self.failed_requests) / self.total_requests) * 100
        
        self.updated_at = datetime.utcnow()
    
    def update_data_metrics(self, record_count: int, data_size: int) -> None:
        """Update data metrics."""
        self.last_record_count = self.record_count
        self.last_data_size = self.data_size
        self.record_count = record_count
        self.data_size = data_size
        self.last_updated = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def schedule_next_update(self, frequency_hours: int = 24) -> None:
        """Schedule next update."""
        from datetime import timedelta
        self.next_update = datetime.utcnow() + timedelta(hours=frequency_hours)
        self.updated_at = datetime.utcnow()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to data source."""
        # This would be implemented based on source type
        # For now, return a mock result
        return {
            "success": True,
            "response_time": 0.5,
            "message": "Connection successful",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with additional properties."""
        result = super().to_dict()
        result.update({
            'connection_string': self.connection_string,
            'is_healthy': self.is_healthy,
            'is_due_for_update': self.is_due_for_update,
            'failure_rate': self.failure_rate,
            'data_growth_rate': self.data_growth_rate
        })
        return result
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<DataSource(id={self.id}, name='{self.name}', type={self.source_type.value})>"
