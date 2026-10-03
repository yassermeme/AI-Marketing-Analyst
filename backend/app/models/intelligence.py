from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AnomalyStatus, InsightType, ProviderType, Severity, SyncJobStatus
from app.models.operational import OrganizationOwned, provider_enum


class SyncJob(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "sync_jobs"
    __table_args__ = (Index("ix_sync_jobs_org_created", "organization_id", "created_at"), Index("ix_sync_jobs_integration_created", "integration_id", "created_at"), Index("ix_sync_jobs_org_status", "organization_id", "status"))
    integration_id: Mapped[UUID] = mapped_column(ForeignKey("integrations.id", ondelete="RESTRICT"), nullable=False)
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    status: Mapped[SyncJobStatus] = mapped_column(Enum(SyncJobStatus, name="sync_job_status"), nullable=False, default=SyncJobStatus.PENDING)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_processed: Mapped[int] = mapped_column(nullable=False, default=0)
    records_created: Mapped[int] = mapped_column(nullable=False, default=0)
    records_updated: Mapped[int] = mapped_column(nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)


class AIInsight(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "ai_insights"
    __table_args__ = (Index("ix_ai_insights_org_created", "organization_id", "created_at"), Index("ix_ai_insights_org_period", "organization_id", "period_start", "period_end"))
    insight_type: Mapped[InsightType] = mapped_column(Enum(InsightType, name="insight_type"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity, name="severity"), nullable=False, default=Severity.INFO)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    context_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class Anomaly(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "anomalies"
    __table_args__ = (Index("ix_anomalies_org_detected", "organization_id", "detected_at"), Index("ix_anomalies_org_metric_period", "organization_id", "metric", "period_start"), Index("ix_anomalies_entity", "organization_id", "entity_type", "entity_id"))
    metric: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column()
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    baseline_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    actual_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    percentage_change: Mapped[Decimal | None] = mapped_column(Numeric(9, 4))
    severity: Mapped[Severity] = mapped_column(Enum(Severity, name="severity"), nullable=False)
    status: Mapped[AnomalyStatus] = mapped_column(Enum(AnomalyStatus, name="anomaly_status"), nullable=False, default=AnomalyStatus.OPEN)
    description: Mapped[str] = mapped_column(Text, nullable=False)
