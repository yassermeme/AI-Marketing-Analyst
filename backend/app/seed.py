"""Deterministic development dataset for local Phase 2 verification.

Run after migrations with: `python -m app.seed`.
"""
import asyncio
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.analytics import DimAd, DimCampaign, DimDate, DimLead, DimMedium, DimSource, FactAdSpend, FactAppointment, FactLead, FactOpportunity, FactQualifiedLead, FactRevenue, FactSale
from app.models.enums import IntegrationStatus, LeadStatus, OpportunityStatus, ProviderType, SaleStatus
from app.models.operational import Ad, Appointment, Campaign, Customer, Integration, Lead, Opportunity, Organization, Revenue, Sale, User

START_DATE = date(2026, 7, 1)
DAYS = 90


def at(day: date, hour: int = 10) -> datetime:
    return datetime.combine(day, time(hour, tzinfo=UTC))


async def seed(session: AsyncSession) -> None:
    if await session.scalar(select(Organization.id).limit(1)):
        return

    for offset in range(DAYS):
        current_date = START_DATE + timedelta(days=offset)
        session.add(DimDate(date=current_date, year=current_date.year, month=current_date.month, day=current_date.day, week=current_date.isocalendar().week))

    organizations = [Organization(name="Northstar Fitness", slug="northstar-fitness"), Organization(name="Harbor Dental", slug="harbor-dental")]
    session.add_all(organizations)
    await session.flush()

    for organization in organizations:
        session.add_all([
            User(organization_id=organization.id, email=f"analyst@{organization.slug}.example", display_name="Analytics Lead"),
            User(organization_id=organization.id, email=f"owner@{organization.slug}.example", display_name="Account Owner"),
        ])

        integrations = [
            Integration(organization_id=organization.id, provider=ProviderType.META_ADS, external_account_id=f"meta-{organization.slug}", status=IntegrationStatus.ACTIVE, credentials_reference="development://mock/meta"),
            Integration(organization_id=organization.id, provider=ProviderType.GOOGLE_ADS, external_account_id=f"google-{organization.slug}", status=IntegrationStatus.ACTIVE, credentials_reference="development://mock/google"),
            Integration(organization_id=organization.id, provider=ProviderType.CRM, external_account_id=f"crm-{organization.slug}", status=IntegrationStatus.ACTIVE, credentials_reference="development://mock/crm"),
        ]
        session.add_all(integrations)
        await session.flush()

        sources = {name: DimSource(organization_id=organization.id, name=name) for name in ("meta", "google", "organic")}
        mediums = {name: DimMedium(organization_id=organization.id, name=name) for name in ("paid_social", "paid_search", "organic")}
        session.add_all([*sources.values(), *mediums.values()])

        campaigns: list[Campaign] = []
        for index in range(6):
            provider = ProviderType.META_ADS if index % 2 == 0 else ProviderType.GOOGLE_ADS
            campaigns.append(Campaign(organization_id=organization.id, integration_id=integrations[0 if provider == ProviderType.META_ADS else 1].id, provider=provider, provider_id=f"{organization.slug}-campaign-{index + 1}", name=f"{['Awareness', 'Demand', 'Retargeting'][index % 3]} {index + 1}", channel="paid_social" if provider == ProviderType.META_ADS else "paid_search", status="ACTIVE"))
        session.add_all(campaigns)
        await session.flush()

        dim_campaigns: dict[int, DimCampaign] = {}
        ads: dict[int, Ad] = {}
        dim_ads: dict[int, DimAd] = {}
        for index, campaign in enumerate(campaigns):
            dimension = DimCampaign(organization_id=organization.id, campaign_id=campaign.id, provider_id=campaign.provider_id, name=campaign.name, channel=campaign.channel)
            ad = Ad(organization_id=organization.id, campaign_id=campaign.id, integration_id=campaign.integration_id, provider=campaign.provider, provider_id=f"{campaign.provider_id}-ad", name=f"{campaign.name} creative")
            session.add_all([dimension, ad])
            await session.flush()
            dim_campaigns[index] = dimension
            ads[index] = ad
            dim_ad = DimAd(organization_id=organization.id, ad_id=ad.id, campaign_dimension_id=dimension.id, provider_id=ad.provider_id, name=ad.name)
            session.add(dim_ad)
            dim_ads[index] = dim_ad
        await session.flush()

        for offset in range(DAYS):
            current_date = START_DATE + timedelta(days=offset)
            for campaign_index, campaign in enumerate(campaigns):
                source_key = "meta" if campaign.provider == ProviderType.META_ADS else "google"
                session.add(FactAdSpend(organization_id=organization.id, date=current_date, campaign_dimension_id=dim_campaigns[campaign_index].id, ad_dimension_id=dim_ads[campaign_index].id, source_dimension_id=sources[source_key].id, provider=campaign.provider.value, provider_id=f"spend-{campaign.provider_id}-{current_date.isoformat()}", spend=Decimal("35.00") + Decimal((offset + campaign_index) % 11), impressions=1000 + ((offset * 37 + campaign_index * 61) % 700), clicks=45 + ((offset + campaign_index * 3) % 31)))

            # Two leads per day and organization: 360 deterministic leads across the dataset.
            for lead_index in range(2):
                campaign_index = (offset * 2 + lead_index) % len(campaigns)
                campaign = campaigns[campaign_index]
                source_key = "meta" if campaign.provider == ProviderType.META_ADS else "google"
                event_at = at(current_date, 9 + lead_index)
                qualified = (offset + lead_index) % 3 != 0
                lead = Lead(organization_id=organization.id, campaign_id=campaign.id, ad_id=ads[campaign_index].id, integration_id=integrations[2].id, provider=ProviderType.CRM, provider_id=f"{organization.slug}-lead-{offset}-{lead_index}", source=source_key, medium="paid_social" if source_key == "meta" else "paid_search", email=f"lead-{offset}-{lead_index}@{organization.slug}.example", status=LeadStatus.QUALIFIED if qualified else LeadStatus.NEW, qualified_at=event_at + timedelta(hours=2) if qualified else None)
                session.add(lead)
                await session.flush()
                dim_lead = DimLead(organization_id=organization.id, lead_id=lead.id, source_dimension_id=sources[source_key].id, medium_dimension_id=mediums["paid_social" if source_key == "meta" else "paid_search"].id, campaign_dimension_id=dim_campaigns[campaign_index].id)
                session.add(dim_lead)
                await session.flush()
                common = dict(organization_id=organization.id, date=current_date, campaign_dimension_id=dim_campaigns[campaign_index].id, ad_dimension_id=dim_ads[campaign_index].id, source_dimension_id=sources[source_key].id, provider="CRM", provider_id=lead.provider_id)
                session.add(FactLead(**common, lead_dimension_id=dim_lead.id, occurred_at=event_at))
                if not qualified:
                    continue
                session.add(FactQualifiedLead(**common, lead_dimension_id=dim_lead.id, qualified_at=lead.qualified_at))
                if offset % 2:
                    continue
                appointment = Appointment(organization_id=organization.id, lead_id=lead.id, provider_id=f"appointment-{lead.provider_id}", scheduled_at=event_at + timedelta(days=1), completed_at=event_at + timedelta(days=1, hours=1), status="COMPLETED")
                session.add(appointment)
                await session.flush()
                session.add(FactAppointment(**common, appointment_id=appointment.id, lead_dimension_id=dim_lead.id, occurred_at=appointment.completed_at))
                if offset % 5:
                    continue
                customer = Customer(organization_id=organization.id, provider=ProviderType.CRM, provider_id=f"customer-{lead.provider_id}", email=lead.email, name=f"Customer {offset}-{lead_index}")
                session.add(customer)
                await session.flush()
                opportunity = Opportunity(organization_id=organization.id, lead_id=lead.id, customer_id=customer.id, provider=ProviderType.CRM, provider_id=f"opportunity-{lead.provider_id}", status=OpportunityStatus.WON, amount=Decimal("1200.00"))
                session.add(opportunity)
                await session.flush()
                session.add(FactOpportunity(**common, opportunity_id=opportunity.id, lead_dimension_id=dim_lead.id, amount=opportunity.amount, occurred_at=event_at + timedelta(days=2)))
                sale = Sale(organization_id=organization.id, opportunity_id=opportunity.id, customer_id=customer.id, provider=ProviderType.ERP, provider_id=f"sale-{lead.provider_id}", sold_at=event_at + timedelta(days=3), status=SaleStatus.COMPLETED, order_value=Decimal("1200.00"))
                session.add(sale)
                await session.flush()
                session.add(FactSale(**common, sale_id=sale.id, amount=sale.order_value, occurred_at=sale.sold_at))
                revenue = Revenue(organization_id=organization.id, sale_id=sale.id, customer_id=customer.id, provider=ProviderType.ERP, provider_id=f"revenue-{lead.provider_id}", recognized_at=sale.sold_at, amount=sale.order_value, currency="USD")
                session.add(revenue)
                await session.flush()
                session.add(FactRevenue(**common, revenue_id=revenue.id, sale_id=sale.id, amount=revenue.amount, recognized_at=revenue.recognized_at))

    await session.commit()


async def main() -> None:
    engine = create_async_engine(get_settings().database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
