from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from flowlens.database import SessionLocal
from flowlens.main import app
from flowlens.models import Organization


client = TestClient(app)


@pytest.fixture
def created_organization_ids() -> Generator[list[UUID], None, None]:
    organization_ids: list[UUID] = []

    yield organization_ids

    if not organization_ids:
        return

    with SessionLocal() as session:
        session.execute(
            delete(Organization).where(
                Organization.id.in_(organization_ids),
            )
        )
        session.commit()


def create_test_organization(
    created_organization_ids: list[UUID],
) -> dict[str, object]:
    identifier = uuid4().hex[:12]

    response = client.post(
        "/organizations",
        json={
            "name": f"Test Organization {identifier}",
            "slug": f"test-organization-{identifier}",
        },
    )

    assert response.status_code == 201

    organization = response.json()
    created_organization_ids.append(
        UUID(organization["id"])
    )

    return organization


def user_payload() -> dict[str, object]:
    identifier = uuid4().hex[:12]

    return {
        "email": f"user-{identifier}@northstar.example",
        "display_name": f"Test User {identifier}",
        "department": "Operations",
        "identity_source": "demo",
    }


def role_payload() -> dict[str, object]:
    identifier = uuid4().hex[:12]

    return {
        "code": f"operations_manager_{identifier}",
        "name": f"Operations Manager {identifier}",
        "description": "Manages workflow operations.",
        "permissions": [
            "work_items:read",
            "work_items:update",
            "exceptions:manage",
        ],
    }


def create_test_user(
    organization_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/organizations/{organization_id}/users",
        json=user_payload(),
    )

    assert response.status_code == 201

    return response.json()


def create_test_role(
    organization_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/organizations/{organization_id}/roles",
        json=role_payload(),
    )

    assert response.status_code == 201

    return response.json()


def test_creates_lists_and_retrieves_user(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])
    payload = user_payload()

    create_response = client.post(
        f"/organizations/{organization_id}/users",
        json=payload,
    )

    assert create_response.status_code == 201

    user = create_response.json()

    assert user["organization_id"] == organization_id
    assert user["email"] == payload["email"]
    assert user["display_name"] == payload["display_name"]
    assert user["department"] == "Operations"
    assert user["identity_source"] == "demo"
    assert user["active"] is True

    list_response = client.get(
        f"/organizations/{organization_id}/users"
    )

    assert list_response.status_code == 200
    assert any(
        listed_user["id"] == user["id"]
        for listed_user in list_response.json()
    )

    retrieve_response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/users/{user['id']}"
        )
    )

    assert retrieve_response.status_code == 200
    assert retrieve_response.json() == user


def test_rejects_duplicate_user_email(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])
    payload = user_payload()

    first_response = client.post(
        f"/organizations/{organization_id}/users",
        json=payload,
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        f"/organizations/{organization_id}/users",
        json={
            **payload,
            "email": str(payload["email"]).upper(),
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": (
            "A user with this email already exists "
            "in the organization."
        )
    }


def test_creates_lists_and_retrieves_role(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])
    payload = role_payload()

    create_response = client.post(
        f"/organizations/{organization_id}/roles",
        json=payload,
    )

    assert create_response.status_code == 201

    role = create_response.json()

    assert role["organization_id"] == organization_id
    assert role["code"] == payload["code"]
    assert role["name"] == payload["name"]
    assert role["permissions"] == sorted(payload["permissions"])
    assert role["active"] is True

    list_response = client.get(
        f"/organizations/{organization_id}/roles"
    )

    assert list_response.status_code == 200
    assert any(
        listed_role["id"] == role["id"]
        for listed_role in list_response.json()
    )

    retrieve_response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/roles/{role['id']}"
        )
    )

    assert retrieve_response.status_code == 200
    assert retrieve_response.json() == role


def test_rejects_duplicate_role_code(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])
    payload = role_payload()

    first_response = client.post(
        f"/organizations/{organization_id}/roles",
        json=payload,
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        f"/organizations/{organization_id}/roles",
        json={
            **payload,
            "name": "Another Role",
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": (
            "A role with this code already exists "
            "in the organization."
        )
    }


def test_assigns_and_lists_user_role(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])
    user = create_test_user(organization_id)
    role = create_test_role(organization_id)

    assignment_response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/users/{user['id']}/roles"
        ),
        json={
            "role_id": role["id"],
            "assigned_by_user_id": user["id"],
        },
    )

    assert assignment_response.status_code == 201

    assignment = assignment_response.json()

    assert assignment["user_id"] == user["id"]
    assert assignment["role_id"] == role["id"]
    assert assignment["assigned_by_user_id"] == user["id"]
    assert assignment["assigned_at"] is not None

    list_response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/users/{user['id']}/roles"
        )
    )

    assert list_response.status_code == 200
    assert list_response.json() == [assignment]


def test_rejects_duplicate_user_role_assignment(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])
    user = create_test_user(organization_id)
    role = create_test_role(organization_id)
    assignment_url = (
        f"/organizations/{organization_id}"
        f"/users/{user['id']}/roles"
    )

    first_response = client.post(
        assignment_url,
        json={
            "role_id": role["id"],
        },
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        assignment_url,
        json={
            "role_id": role["id"],
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": "The user already has this role."
    }


def test_rejects_role_from_another_organization(
    created_organization_ids: list[UUID],
) -> None:
    first_organization = create_test_organization(
        created_organization_ids
    )
    second_organization = create_test_organization(
        created_organization_ids
    )
    first_organization_id = str(first_organization["id"])
    second_organization_id = str(second_organization["id"])
    user = create_test_user(first_organization_id)
    other_role = create_test_role(second_organization_id)

    response = client.post(
        (
            f"/organizations/{first_organization_id}"
            f"/users/{user['id']}/roles"
        ),
        json={
            "role_id": other_role["id"],
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Role not found."
    }


def test_returns_404_for_missing_organization() -> None:
    response = client.get(
        f"/organizations/{uuid4()}/users"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Organization not found."
    }