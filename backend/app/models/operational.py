from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import IntegrationStatus, LeadStatus, OpportunityStatus, ProviderType, SaleStatus

provider_enum = Enum(ProviderType, name="provider_type")


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("slug", name="uq_organizations_slug"),)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="organization")


class OrganizationOwned:
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)


class User(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("organization_id", "email", name="uq_users_organization_email"), Index("ix_users_organization_created", "organization_id", "created_at"))
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization: Mapped[Organization] = relationship(back_populates="users")


class Integration(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "integrations"
    __table_args__ = (UniqueConstraint("organization_id", "provider", "external_account_id", name="uq_integrations_org_provider_account"), Index("ix_integrations_organization_provider", "organization_id", "provider"))
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    status: Mapped[IntegrationStatus] = mapped_column(Enum(IntegrationStatus, name="integration_status"), nullable=False, default=IntegrationStatus.ACTIVE)
    external_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    credentials_reference: Mapped[str | None] = mapped_column(String(512))
    configuration: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Campaign(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "campaigns"
    __table_args__ = (UniqueConstraint("organization_id", "provider", "provider_id", name="uq_campaigns_org_provider_id"), Index("ix_campaigns_organization_provider", "organization_id", "provider"))
    integration_id: Mapped[UUID | None] = mapped_column(ForeignKey("integrations.id", ondelete="SET NULL"))
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    channel: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str | None] = mapped_column(String(100))


class Ad(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "ads"
    __table_args__ = (UniqueConstraint("organization_id", "provider", "provider_id", name="uq_ads_org_provider_id"), Index("ix_ads_organization_campaign", "organization_id", "campaign_id"))
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    integration_id: Mapped[UUID | None] = mapped_column(ForeignKey("integrations.id", ondelete="SET NULL"))
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    ad_set_provider_id: Mapped[str | None] = mapped_column(String(255))


class Lead(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "leads"
    __table_args__ = (UniqueConstraint("organization_id", "provider", "provider_id", name="uq_leads_org_provider_id"), Index("ix_leads_organization_created", "organization_id", "created_at"), Index("ix_leads_organization_campaign", "organization_id", "campaign_id"), Index("ix_leads_organization_source", "organization_id", "source"))
    campaign_id: Mapped[UUID | None] = mapped_column(ForeignKey("campaigns.id", ondelete="SET NULL"))
    ad_id: Mapped[UUID | None] = mapped_column(ForeignKey("ads.id", ondelete="SET NULL"))
    integration_id: Mapped[UUID | None] = mapped_column(ForeignKey("integrations.id", ondelete="SET NULL"))
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    medium: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(320))
    status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus, name="lead_status"), nullable=False, default=LeadStatus.NEW)
    qualified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Customer(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("organization_id", "provider", "provider_id", name="uq_customers_org_provider_id"), Index("ix_customers_organization_created", "organization_id", "created_at"))
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    name: Mapped[str | None] = mapped_column(String(255))


class Appointment(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "appointments"
    __table_args__ = (Index("ix_appointments_organization_scheduled", "organization_id", "scheduled_at"),)
    lead_id: Mapped[UUID] = mapped_column(ForeignKey("leads.id", ondelete="RESTRICT"), nullable=False)
    provider_id: Mapped[str | None] = mapped_column(String(255))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(100), nullable=False)


class Opportunity(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "opportunities"
    __table_args__ = (UniqueConstraint("organization_id", "provider", "provider_id", name="uq_opportunities_org_provider_id"), Index("ix_opportunities_organization_created", "organization_id", "created_at"))
    lead_id: Mapped[UUID | None] = mapped_column(ForeignKey("leads.id", ondelete="SET NULL"))
    customer_id: Mapped[UUID | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"))
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[OpportunityStatus] = mapped_column(Enum(OpportunityStatus, name="opportunity_status"), nullable=False, default=OpportunityStatus.OPEN)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))


class Sale(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "sales"
    __table_args__ = (UniqueConstraint("organization_id", "provider", "provider_id", name="uq_sales_org_provider_id"), Index("ix_sales_organization_occurred", "organization_id", "sold_at"))
    opportunity_id: Mapped[UUID | None] = mapped_column(ForeignKey("opportunities.id", ondelete="SET NULL"))
    customer_id: Mapped[UUID | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"))
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    sold_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[SaleStatus] = mapped_column(Enum(SaleStatus, name="sale_status"), nullable=False, default=SaleStatus.COMPLETED)
    order_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)


class Revenue(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "revenues"
    __table_args__ = (UniqueConstraint("organization_id", "provider", "provider_id", name="uq_revenues_org_provider_id"), CheckConstraint("amount >= 0", name="ck_revenues_amount_nonnegative"), Index("ix_revenues_organization_recognized", "organization_id", "recognized_at"))
    sale_id: Mapped[UUID | None] = mapped_column(ForeignKey("sales.id", ondelete="SET NULL"))
    customer_id: Mapped[UUID | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"))
    provider: Mapped[ProviderType] = mapped_column(provider_enum, nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    recognized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
