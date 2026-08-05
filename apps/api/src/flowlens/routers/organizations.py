from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from flowlens.database import get_database_session
from flowlens.models import Organization
from flowlens.schemas import OrganizationCreate, OrganizationResponse
from flowlens.services.organizations import (
    create_organization,
    get_organization,
    get_organization_by_slug,
    list_organizations,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_database_session),
]


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an organization",
)
def create_organization_endpoint(
    organization_data: OrganizationCreate,
    session: DatabaseSession,
) -> Organization:
    existing_organization = get_organization_by_slug(
        session,
        organization_data.slug,
    )

    if existing_organization is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this slug already exists.",
        )

    try:
        return create_organization(
            session,
            organization_data,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this slug already exists.",
        ) from exc


@router.get(
    "",
    response_model=list[OrganizationResponse],
    summary="List organizations",
)
def list_organizations_endpoint(
    session: DatabaseSession,
) -> list[Organization]:
    return list_organizations(session)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Retrieve an organization",
)
def get_organization_endpoint(
    organization_id: UUID,
    session: DatabaseSession,
) -> Organization:
    organization = get_organization(
        session,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return organization