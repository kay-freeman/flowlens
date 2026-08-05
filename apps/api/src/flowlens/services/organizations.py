from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from flowlens.models import Organization
from flowlens.schemas import OrganizationCreate


def create_organization(
    session: Session,
    organization_data: OrganizationCreate,
) -> Organization:
    organization = Organization(
        name=organization_data.name,
        slug=organization_data.slug,
    )

    session.add(organization)
    session.commit()
    session.refresh(organization)

    return organization


def list_organizations(
    session: Session,
) -> list[Organization]:
    statement = select(Organization).order_by(Organization.name)

    return list(session.scalars(statement).all())


def get_organization(
    session: Session,
    organization_id: UUID,
) -> Organization | None:
    return session.get(Organization, organization_id)


def get_organization_by_slug(
    session: Session,
    slug: str,
) -> Organization | None:
    statement = select(Organization).where(
        Organization.slug == slug,
    )

    return session.scalar(statement)