from enum import StrEnum


class ProviderType(StrEnum):
    META_ADS = "META_ADS"
    GOOGLE_ADS = "GOOGLE_ADS"
    CRM = "CRM"
    ERP = "ERP"
    WEBSITE = "WEBSITE"


class IntegrationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"


class SyncJobStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class LeadStatus(StrEnum):
    NEW = "NEW"
    QUALIFIED = "QUALIFIED"
    DISQUALIFIED = "DISQUALIFIED"


class OpportunityStatus(StrEnum):
    OPEN = "OPEN"
    WON = "WON"
    LOST = "LOST"


class SaleStatus(StrEnum):
    COMPLETED = "COMPLETED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class InsightType(StrEnum):
    PERFORMANCE = "PERFORMANCE"
    ANOMALY = "ANOMALY"
    CAMPAIGN = "CAMPAIGN"
    FUNNEL = "FUNNEL"
    REVENUE = "REVENUE"


class Severity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyStatus(StrEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
