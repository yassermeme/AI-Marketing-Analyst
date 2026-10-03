from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.operational import OrganizationOwned


class DimDate(Base):
    __tablename__ = "dim_date"
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)


class DimCampaign(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "dim_campaign"
    __table_args__ = (UniqueConstraint("organization_id", "campaign_id", name="uq_dim_campaign_org_campaign"),)
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    channel: Mapped[str | None] = mapped_column(String(100))


class DimAd(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "dim_ad"
    __table_args__ = (UniqueConstraint("organization_id", "ad_id", name="uq_dim_ad_org_ad"),)
    ad_id: Mapped[UUID] = mapped_column(ForeignKey("ads.id", ondelete="CASCADE"), nullable=False)
    campaign_dimension_id: Mapped[UUID] = mapped_column(ForeignKey("dim_campaign.id", ondelete="RESTRICT"), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)


class DimSource(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "dim_source"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_dim_source_org_name"),)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class DimMedium(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "dim_medium"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_dim_medium_org_name"),)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class DimLead(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "dim_lead"
    __table_args__ = (UniqueConstraint("organization_id", "lead_id", name="uq_dim_lead_org_lead"),)
    lead_id: Mapped[UUID] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    source_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_source.id", ondelete="SET NULL"))
    medium_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_medium.id", ondelete="SET NULL"))
    campaign_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_campaign.id", ondelete="SET NULL"))


class DimCustomer(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "dim_customer"
    __table_args__ = (UniqueConstraint("organization_id", "customer_id", name="uq_dim_customer_org_customer"),)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)


class DimProduct(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "dim_product"
    __table_args__ = (UniqueConstraint("organization_id", "provider_id", name="uq_dim_product_org_provider_id"),)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class DimSalesperson(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned, Base):
    __tablename__ = "dim_salesperson"
    __table_args__ = (UniqueConstraint("organization_id", "provider_id", name="uq_dim_salesperson_org_provider_id"),)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class FactBase(UUIDPrimaryKeyMixin, TimestampMixin, OrganizationOwned):
    date: Mapped[date] = mapped_column(ForeignKey("dim_date.date", ondelete="RESTRICT"), nullable=False)
    campaign_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_campaign.id", ondelete="SET NULL"))
    ad_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_ad.id", ondelete="SET NULL"))
    source_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_source.id", ondelete="SET NULL"))
    provider: Mapped[str | None] = mapped_column(String(50))
    provider_id: Mapped[str | None] = mapped_column(String(255))


class FactAdSpend(FactBase, Base):
    __tablename__ = "fact_ad_spend"
    __table_args__ = (CheckConstraint("spend >= 0 AND impressions >= 0 AND clicks >= 0", name="ck_fact_ad_spend_nonnegative"), Index("ix_fact_ad_spend_org_date", "organization_id", "date"), Index("ix_fact_ad_spend_org_campaign", "organization_id", "campaign_dimension_id"), Index("ix_fact_ad_spend_provider_external", "provider", "provider_id"))
    spend: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")


class FactLead(FactBase, Base):
    __tablename__ = "fact_lead"
    __table_args__ = (UniqueConstraint("organization_id", "lead_dimension_id", name="uq_fact_lead_org_dim_lead"), Index("ix_fact_lead_org_date", "organization_id", "date"), Index("ix_fact_lead_org_source", "organization_id", "source_dimension_id"))
    lead_dimension_id: Mapped[UUID] = mapped_column(ForeignKey("dim_lead.id", ondelete="RESTRICT"), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FactQualifiedLead(FactBase, Base):
    __tablename__ = "fact_qualified_lead"
    __table_args__ = (UniqueConstraint("organization_id", "lead_dimension_id", name="uq_fact_qualified_lead_org_dim_lead"), Index("ix_fact_qualified_lead_org_date", "organization_id", "date"))
    lead_dimension_id: Mapped[UUID] = mapped_column(ForeignKey("dim_lead.id", ondelete="RESTRICT"), nullable=False)
    qualified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FactAppointment(FactBase, Base):
    __tablename__ = "fact_appointment"
    __table_args__ = (UniqueConstraint("organization_id", "appointment_id", name="uq_fact_appointment_org_appointment"), Index("ix_fact_appointment_org_date", "organization_id", "date"))
    appointment_id: Mapped[UUID] = mapped_column(ForeignKey("appointments.id", ondelete="RESTRICT"), nullable=False)
    lead_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_lead.id", ondelete="SET NULL"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FactOpportunity(FactBase, Base):
    __tablename__ = "fact_opportunity"
    __table_args__ = (UniqueConstraint("organization_id", "opportunity_id", name="uq_fact_opportunity_org_opportunity"), Index("ix_fact_opportunity_org_date", "organization_id", "date"))
    opportunity_id: Mapped[UUID] = mapped_column(ForeignKey("opportunities.id", ondelete="RESTRICT"), nullable=False)
    lead_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_lead.id", ondelete="SET NULL"))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FactSale(FactBase, Base):
    __tablename__ = "fact_sale"
    __table_args__ = (UniqueConstraint("organization_id", "sale_id", name="uq_fact_sale_org_sale"), Index("ix_fact_sale_org_date", "organization_id", "date"))
    sale_id: Mapped[UUID] = mapped_column(ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False)
    customer_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_customer.id", ondelete="SET NULL"))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FactRevenue(FactBase, Base):
    __tablename__ = "fact_revenue"
    __table_args__ = (UniqueConstraint("organization_id", "revenue_id", name="uq_fact_revenue_org_revenue"), Index("ix_fact_revenue_org_date", "organization_id", "date"))
    revenue_id: Mapped[UUID] = mapped_column(ForeignKey("revenues.id", ondelete="RESTRICT"), nullable=False)
    sale_id: Mapped[UUID | None] = mapped_column(ForeignKey("sales.id", ondelete="SET NULL"))
    customer_dimension_id: Mapped[UUID | None] = mapped_column(ForeignKey("dim_customer.id", ondelete="SET NULL"))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    recognized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
