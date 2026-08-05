from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from flowlens.database import get_database_session
from flowlens.models import Role, UserRole
from flowlens.schemas import (
    RoleCreate,
    RoleResponse,
    UserRoleCreate,
    UserRoleResponse,
)
from flowlens.services.organizations import get_organization
from flowlens.services.roles import (
    assign_role_to_user,
    create_role,
    get_role,
    get_role_by_code,
    get_user_role_assignment,
    list_roles,
    list_user_role_assignments,
)
from flowlens.services.users import get_user


router = APIRouter(
    prefix="/organizations/{organization_id}",
    tags=["Roles"],
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
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a role",
)
def create_role_endpoint(
    organization_id: UUID,
    role_data: RoleCreate,
    session: DatabaseSession,
) -> Role:
    require_organization(
        session,
        organization_id,
    )

    existing_role = get_role_by_code(
        session,
        organization_id,
        role_data.code,
    )

    if existing_role is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A role with this code already exists "
                "in the organization."
            ),
        )

    try:
        return create_role(
            session,
            organization_id,
            role_data,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A role with this code already exists "
                "in the organization."
            ),
        ) from exc


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    summary="List roles",
)
def list_roles_endpoint(
    organization_id: UUID,
    session: DatabaseSession,
) -> list[Role]:
    require_organization(
        session,
        organization_id,
    )

    return list_roles(
        session,
        organization_id,
    )


@router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Retrieve a role",
)
def get_role_endpoint(
    organization_id: UUID,
    role_id: UUID,
    session: DatabaseSession,
) -> Role:
    require_organization(
        session,
        organization_id,
    )

    role = get_role(
        session,
        organization_id,
        role_id,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    return role


@router.post(
    "/users/{user_id}/roles",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a role to a user",
)
def assign_role_endpoint(
    organization_id: UUID,
    user_id: UUID,
    assignment_data: UserRoleCreate,
    session: DatabaseSession,
) -> UserRole:
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

    role = get_role(
        session,
        organization_id,
        assignment_data.role_id,
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    if assignment_data.assigned_by_user_id is not None:
        assigning_user = get_user(
            session,
            organization_id,
            assignment_data.assigned_by_user_id,
        )

        if assigning_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigning user not found.",
            )

    existing_assignment = get_user_role_assignment(
        session,
        user_id,
        assignment_data.role_id,
    )

    if existing_assignment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user already has this role.",
        )

    try:
        return assign_role_to_user(
            session,
            user_id,
            assignment_data.role_id,
            assignment_data.assigned_by_user_id,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user already has this role.",
        ) from exc


@router.get(
    "/users/{user_id}/roles",
    response_model=list[UserRoleResponse],
    summary="List a user's role assignments",
)
def list_user_roles_endpoint(
    organization_id: UUID,
    user_id: UUID,
    session: DatabaseSession,
) -> list[UserRole]:
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

    return list_user_role_assignments(
        session,
        user_id,
    )