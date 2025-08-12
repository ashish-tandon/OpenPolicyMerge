"""
Data Quality Metric model for tracking data quality metrics.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import enum

from .base import Base


class MetricType(enum.Enum):
    """Data quality metric type enumeration."""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    INTEGRITY = "integrity"
    CUSTOM = "custom"


class MetricStatus(enum.Enum):
    """Metric status enumeration."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    UNKNOWN = "unknown"


class DataQualityMetric(Base):
    """Data Quality Metric model for tracking data quality metrics."""
    
    __tablename__ = "data_quality_metrics"
    
    # Metric identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    status = Column(Enum(MetricStatus), default=MetricStatus.UNKNOWN, index=True)
    
    # Metric values
    current_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    target_value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)  # percentage, count, etc.
    
    # Calculation details
    calculation_method = Column(String(255), nullable=True)
    calculation_formula = Column(Text, nullable=True)
    sample_size = Column(Integer, nullable=True)
    
    # Timing
    measured_at = Column(DateTime, nullable=True)
    next_measurement = Column(DateTime, nullable=True)
    measurement_frequency = Column(String(100), nullable=True)  # Daily, hourly, etc.
    
    # Historical data
    historical_values = Column(JSON, nullable=True)  # Array of historical measurements
    trend = Column(String(50), nullable=True)  # improving, declining, stable
    
    # Thresholds and alerts
    warning_threshold = Column(Float, nullable=True)
    critical_threshold = Column(Float, nullable=True)
    alert_enabled = Column(Boolean, default=True)
    
    # Relationships
    data_source_id = Column(String(36), ForeignKey("datasources.id"), nullable=True)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="quality_metrics")
    
    def __init__(self, **kwargs):
        """Initialize Data Quality Metric with UUID."""
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    @property
    def is_healthy(self) -> bool:
        """Check if metric is healthy (passing thresholds)."""
        if self.status == MetricStatus.PASS:
            return True
        return False
    
    @property
    def needs_attention(self) -> bool:
        """Check if metric needs attention."""
        return self.status in [MetricStatus.WARNING, MetricStatus.FAIL]
    
    @property
    def trend_direction(self) -> str:
        """Get trend direction based on historical values."""
        if not self.historical_values or len(self.historical_values) < 2:
            return "unknown"
        
        # Simple trend calculation
        recent_values = self.historical_values[-5:]  # Last 5 values
        if len(recent_values) < 2:
            return "unknown"
        
        first_value = recent_values[0]
        last_value = recent_values[-1]
        
        if last_value > first_value:
            return "improving"
        elif last_value < first_value:
            return "declining"
        else:
            return "stable"
    
    def calculate_status(self) -> MetricStatus:
        """Calculate metric status based on thresholds."""
        if self.current_value is None:
            return MetricStatus.UNKNOWN
        
        if self.critical_threshold is not None and self.current_value <= self.critical_threshold:
            return MetricStatus.FAIL
        elif self.warning_threshold is not None and self.current_value <= self.warning_threshold:
            return MetricStatus.WARNING
        elif self.threshold_value is not None and self.current_value >= self.threshold_value:
            return MetricStatus.PASS
        else:
            return MetricStatus.UNKNOWN
    
    def update_measurement(self, value: float, measured_at: datetime = None) -> None:
        """Update metric measurement."""
        self.current_value = value
        self.measured_at = measured_at or datetime.utcnow()
        
        # Update status
        self.status = self.calculate_status()
        
        # Add to historical values
        if self.historical_values is None:
            self.historical_values = []
        
        self.historical_values.append({
            "value": value,
            "timestamp": self.measured_at.isoformat(),
            "status": self.status.value
        })
        
        # Keep only last 100 measurements
        if len(self.historical_values) > 100:
            self.historical_values = self.historical_values[-100:]
        
        # Update trend
        self.trend = self.trend_direction
        
        self.updated_at = datetime.utcnow()
    
    def set_thresholds(self, warning: float = None, critical: float = None, target: float = None) -> None:
        """Set metric thresholds."""
        if warning is not None:
            self.warning_threshold = warning
        if critical is not None:
            self.critical_threshold = critical
        if target is not None:
            self.target_value = target
        
        # Recalculate status
        self.status = self.calculate_status()
        self.updated_at = datetime.utcnow()
    
    def get_performance_score(self) -> float:
        """Calculate performance score (0-100)."""
        if self.current_value is None or self.target_value is None:
            return 0.0
        
        if self.target_value == 0:
            return 0.0
        
        # Calculate score based on how close current value is to target
        score = (self.current_value / self.target_value) * 100
        return min(100.0, max(0.0, score))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with additional properties."""
        result = super().to_dict()
        result.update({
            'is_healthy': self.is_healthy,
            'needs_attention': self.needs_attention,
            'trend_direction': self.trend_direction,
            'performance_score': self.get_performance_score()
        })
        return result
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<DataQualityMetric(id={self.id}, name='{self.name}', status={self.status.value})>"
