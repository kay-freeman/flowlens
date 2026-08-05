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


def organization_payload() -> dict[str, str]:
    identifier = uuid4().hex[:12]

    return {
        "name": f"Test Organization {identifier}",
        "slug": f"test-organization-{identifier}",
    }


def test_creates_organization(
    created_organization_ids: list[UUID],
) -> None:
    payload = organization_payload()

    response = client.post(
        "/organizations",
        json=payload,
    )

    assert response.status_code == 201

    organization = response.json()
    created_organization_ids.append(UUID(organization["id"]))

    assert organization["name"] == payload["name"]
    assert organization["slug"] == payload["slug"]
    assert organization["is_active"] is True
    assert organization["created_at"] is not None
    assert organization["updated_at"] is not None


def test_lists_organizations(
    created_organization_ids: list[UUID],
) -> None:
    payload = organization_payload()

    create_response = client.post(
        "/organizations",
        json=payload,
    )
    created_organization = create_response.json()
    created_organization_ids.append(
        UUID(created_organization["id"])
    )

    response = client.get("/organizations")

    assert response.status_code == 200
    assert any(
        organization["id"] == created_organization["id"]
        for organization in response.json()
    )


def test_retrieves_organization(
    created_organization_ids: list[UUID],
) -> None:
    payload = organization_payload()

    create_response = client.post(
        "/organizations",
        json=payload,
    )
    created_organization = create_response.json()
    created_organization_ids.append(
        UUID(created_organization["id"])
    )

    response = client.get(
        f"/organizations/{created_organization['id']}"
    )

    assert response.status_code == 200
    assert response.json() == created_organization


def test_rejects_duplicate_organization_slug(
    created_organization_ids: list[UUID],
) -> None:
    payload = organization_payload()

    first_response = client.post(
        "/organizations",
        json=payload,
    )
    created_organization_ids.append(
        UUID(first_response.json()["id"])
    )

    duplicate_response = client.post(
        "/organizations",
        json={
            "name": "Another Organization",
            "slug": payload["slug"],
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": "An organization with this slug already exists.",
    }


def test_returns_404_for_missing_organization() -> None:
    response = client.get(
        f"/organizations/{uuid4()}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Organization not found.",
    }