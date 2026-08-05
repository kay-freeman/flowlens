from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from flowlens.models import User
from flowlens.schemas import UserCreate


def create_user(
    session: Session,
    organization_id: UUID,
    user_data: UserCreate,
) -> User:
    user = User(
        organization_id=organization_id,
        email=user_data.email,
        display_name=user_data.display_name,
        department=user_data.department,
        identity_source=user_data.identity_source.value,
        external_subject=user_data.external_subject,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def list_users(
    session: Session,
    organization_id: UUID,
) -> list[User]:
    statement = (
        select(User)
        .where(User.organization_id == organization_id)
        .order_by(User.display_name, User.email)
    )

    return list(session.scalars(statement).all())


def get_user(
    session: Session,
    organization_id: UUID,
    user_id: UUID,
) -> User | None:
    statement = select(User).where(
        User.organization_id == organization_id,
        User.id == user_id,
    )

    return session.scalar(statement)


def get_user_by_email(
    session: Session,
    organization_id: UUID,
    email: str,
) -> User | None:
    statement = select(User).where(
        User.organization_id == organization_id,
        User.email == email,
    )

    return session.scalar(statement)