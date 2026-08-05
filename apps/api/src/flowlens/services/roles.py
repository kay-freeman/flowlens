from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from flowlens.models import Role, UserRole
from flowlens.schemas import RoleCreate


def create_role(
    session: Session,
    organization_id: UUID,
    role_data: RoleCreate,
) -> Role:
    role = Role(
        organization_id=organization_id,
        code=role_data.code,
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions,
    )

    session.add(role)
    session.commit()
    session.refresh(role)

    return role


def list_roles(
    session: Session,
    organization_id: UUID,
) -> list[Role]:
    statement = (
        select(Role)
        .where(Role.organization_id == organization_id)
        .order_by(Role.name, Role.code)
    )

    return list(session.scalars(statement).all())


def get_role(
    session: Session,
    organization_id: UUID,
    role_id: UUID,
) -> Role | None:
    statement = select(Role).where(
        Role.organization_id == organization_id,
        Role.id == role_id,
    )

    return session.scalar(statement)


def get_role_by_code(
    session: Session,
    organization_id: UUID,
    code: str,
) -> Role | None:
    statement = select(Role).where(
        Role.organization_id == organization_id,
        Role.code == code,
    )

    return session.scalar(statement)


def assign_role_to_user(
    session: Session,
    user_id: UUID,
    role_id: UUID,
    assigned_by_user_id: UUID | None,
) -> UserRole:
    assignment = UserRole(
        user_id=user_id,
        role_id=role_id,
        assigned_by_user_id=assigned_by_user_id,
    )

    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    return assignment


def list_user_role_assignments(
    session: Session,
    user_id: UUID,
) -> list[UserRole]:
    statement = (
        select(UserRole)
        .where(UserRole.user_id == user_id)
        .order_by(UserRole.assigned_at, UserRole.id)
    )

    return list(session.scalars(statement).all())


def get_user_role_assignment(
    session: Session,
    user_id: UUID,
    role_id: UUID,
) -> UserRole | None:
    statement = select(UserRole).where(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
    )

    return session.scalar(statement)