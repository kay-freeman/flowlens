from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from flowlens.schemas import (
    IdentitySource,
    RoleCreate,
    RoleResponse,
    UserCreate,
    UserResponse,
    UserRoleCreate,
    UserRoleResponse,
)


def test_accepts_and_normalizes_valid_user_input() -> None:
    user = UserCreate(
        email="  MAYA.CHEN@NORTHSTAR.EXAMPLE  ",
        display_name="  Maya Chen  ",
        department="  Operations  ",
    )

    assert user.email == "maya.chen@northstar.example"
    assert user.display_name == "Maya Chen"
    assert user.department == "Operations"
    assert user.identity_source == IdentitySource.DEMO
    assert user.external_subject is None


@pytest.mark.parametrize(
    "email",
    [
        "missing-at-sign.example",
        "missing-domain@",
        "@missing-user.example",
        "contains space@example.com",
    ],
)
def test_rejects_invalid_user_emails(email: str) -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            email=email,
            display_name="Maya Chen",
        )


def test_rejects_invalid_identity_source() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            email="maya.chen@northstar.example",
            display_name="Maya Chen",
            identity_source="unsupported",
        )


def test_converts_blank_department_to_none() -> None:
    user = UserCreate(
        email="maya.chen@northstar.example",
        display_name="Maya Chen",
        department="   ",
    )

    assert user.department is None


def test_accepts_and_normalizes_valid_role_input() -> None:
    role = RoleCreate(
        code="  OPERATIONS_MANAGER  ",
        name="  Operations Manager  ",
        description="  Manages workflow operations.  ",
        permissions=[
            "WORK_ITEMS:READ",
            "work_items:read",
            "  exceptions:manage  ",
        ],
    )

    assert role.code == "operations_manager"
    assert role.name == "Operations Manager"
    assert role.description == "Manages workflow operations."
    assert role.permissions == [
        "exceptions:manage",
        "work_items:read",
    ]


def test_normalizes_mixed_case_role_code() -> None:
    role = RoleCreate(
        code="OperationsManager",
        name="Operations Manager",
        description="Manages workflow operations.",
    )

    assert role.code == "operationsmanager"


@pytest.mark.parametrize(
    "code",
    [
        "operations-manager",
        "operations manager",
        "_operations_manager",
        "123_manager",
        "operations.manager",
    ],
)
def test_rejects_invalid_role_codes(code: str) -> None:
    with pytest.raises(ValidationError):
        RoleCreate(
            code=code,
            name="Operations Manager",
            description="Manages workflow operations.",
        )


def test_builds_user_response() -> None:
    now = datetime.now(UTC)
    organization_id = uuid4()

    user_record = SimpleNamespace(
        id=uuid4(),
        organization_id=organization_id,
        email="maya.chen@northstar.example",
        display_name="Maya Chen",
        department="Operations",
        identity_source="demo",
        external_subject=None,
        active=True,
        created_at=now,
        updated_at=now,
    )

    response = UserResponse.model_validate(user_record)

    assert response.id == user_record.id
    assert response.organization_id == organization_id
    assert response.identity_source == IdentitySource.DEMO
    assert response.active is True


def test_builds_role_response() -> None:
    organization_id = uuid4()

    role_record = SimpleNamespace(
        id=uuid4(),
        organization_id=organization_id,
        code="operations_manager",
        name="Operations Manager",
        description="Manages workflow operations.",
        permissions=[
            "work_items:read",
            "work_items:update",
        ],
        active=True,
    )

    response = RoleResponse.model_validate(role_record)

    assert response.id == role_record.id
    assert response.organization_id == organization_id
    assert response.permissions == [
        "work_items:read",
        "work_items:update",
    ]


def test_accepts_user_role_assignment_input() -> None:
    role_id = uuid4()
    assigning_user_id = uuid4()

    assignment = UserRoleCreate(
        role_id=role_id,
        assigned_by_user_id=assigning_user_id,
    )

    assert assignment.role_id == role_id
    assert assignment.assigned_by_user_id == assigning_user_id


def test_builds_user_role_response() -> None:
    now = datetime.now(UTC)

    assignment_record = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        role_id=uuid4(),
        assigned_at=now,
        assigned_by_user_id=None,
    )

    response = UserRoleResponse.model_validate(
        assignment_record
    )

    assert response.id == assignment_record.id
    assert response.user_id == assignment_record.user_id
    assert response.role_id == assignment_record.role_id
    assert response.assigned_at == now
    assert response.assigned_by_user_id is None