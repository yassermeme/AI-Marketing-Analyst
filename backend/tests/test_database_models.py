import asyncio
from uuid import uuid4

import pytest

from sqlalchemy import event, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base
from app.models.analytics import FactLead
from app.models.enums import ProviderType
from app.models.operational import Campaign, Lead, Organization
from app.seed import seed


def run(coroutine):
    return asyncio.run(coroutine)


async def create_session() -> tuple[AsyncSession, object]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    @event.listens_for(engine.sync_engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session = async_sessionmaker(engine, expire_on_commit=False)()
    return session, engine


def test_organization_scoped_unique_constraint_and_tenant_filtering() -> None:
    async def scenario() -> None:
        session, engine = await create_session()
        try:
            first = Organization(name="First", slug="first")
            second = Organization(name="Second", slug="second")
            session.add_all([first, second])
            await session.flush()
            session.add_all([
                Campaign(organization_id=first.id, provider=ProviderType.META_ADS, provider_id="campaign-1", name="First campaign"),
                Campaign(organization_id=second.id, provider=ProviderType.META_ADS, provider_id="campaign-1", name="Second campaign"),
            ])
            await session.commit()

            result = await session.scalars(select(Campaign).where(Campaign.organization_id == first.id))
            assert [campaign.name for campaign in result] == ["First campaign"]

            session.add(Campaign(organization_id=first.id, provider=ProviderType.META_ADS, provider_id="campaign-1", name="Duplicate"))
            with pytest.raises(IntegrityError):
                await session.commit()
        finally:
            await session.close()
            await engine.dispose()

    run(scenario())


def test_foreign_keys_and_required_fields_are_enforced() -> None:
    async def scenario() -> None:
        session, engine = await create_session()
        try:
            organization = Organization(name="Tenant", slug="tenant")
            session.add(organization)
            await session.flush()
            session.add(Lead(organization_id=organization.id, campaign_id=uuid4(), provider=ProviderType.CRM, provider_id="missing-campaign-lead", source="crm"))
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()

            session.add(Lead(organization_id=organization.id, provider=ProviderType.CRM, provider_id="missing-required-source"))  # type: ignore[call-arg]
            with pytest.raises(IntegrityError):
                await session.commit()
        finally:
            await session.close()
            await engine.dispose()

    run(scenario())


def test_deterministic_seed_creates_tenant_scoped_analytical_data() -> None:
    async def scenario() -> None:
        session, engine = await create_session()
        try:
            await seed(session)
            organizations = list(await session.scalars(select(Organization).order_by(Organization.slug)))
            assert len(organizations) == 2
            campaign_count = await session.scalar(select(func.count()).select_from(Campaign))
            lead_count = await session.scalar(select(func.count()).select_from(Lead))
            fact_lead_count = await session.scalar(select(func.count()).select_from(FactLead))
            assert campaign_count == 12
            assert lead_count == 360
            assert fact_lead_count == 360

            first_org_count = await session.scalar(select(func.count()).select_from(FactLead).where(FactLead.organization_id == organizations[0].id))
            assert first_org_count == 180
        finally:
            await session.close()
            await engine.dispose()

    run(scenario())
