from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from flowlens.database import get_database_session
from flowlens.models import User
from flowlens.schemas import UserCreate, UserResponse
from flowlens.services.organizations import get_organization
from flowlens.services.users import (
    create_user,
    get_user,
    get_user_by_email,
    list_users,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/users",
    tags=["Users"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_database_session),
]


def require_organization(
    session: Session,
    organization_id: UUID,
) -> None:
    organization = get_organization(
        session,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
def create_user_endpoint(
    organization_id: UUID,
    user_data: UserCreate,
    session: DatabaseSession,
) -> User:
    require_organization(
        session,
        organization_id,
    )

    existing_user = get_user_by_email(
        session,
        organization_id,
        user_data.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A user with this email already exists "
                "in the organization."
            ),
        )

    try:
        return create_user(
            session,
            organization_id,
            user_data,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A user with this email already exists "
                "in the organization."
            ),
        ) from exc


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List users",
)
def list_users_endpoint(
    organization_id: UUID,
    session: DatabaseSession,
) -> list[User]:
    require_organization(
        session,
        organization_id,
    )

    return list_users(
        session,
        organization_id,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Retrieve a user",
)
def get_user_endpoint(
    organization_id: UUID,
    user_id: UUID,
    session: DatabaseSession,
) -> User:
    require_organization(
        session,
        organization_id,
    )

    user = get_user(
        session,
        organization_id,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user