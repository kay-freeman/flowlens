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
def created_organization_ids() -> Generator[
    list[UUID],
    None,
    None,
]:
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


def workflow_template_payload(
    slug: str | None = None,
) -> dict[str, str]:
    identifier = uuid4().hex[:12]

    return {
        "slug": slug or f"test-workflow-{identifier}",
        "name": f"Test Workflow {identifier}",
        "work_item_label": "Request",
        "work_item_label_plural": "Requests",
        "description": "Coordinates a synthetic test workflow.",
    }


def create_test_organization(
    created_organization_ids: list[UUID],
) -> dict[str, object]:
    response = client.post(
        "/organizations",
        json=organization_payload(),
    )

    assert response.status_code == 201

    organization = response.json()
    created_organization_ids.append(
        UUID(organization["id"])
    )

    return organization


def test_creates_workflow_template(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids,
    )
    payload = workflow_template_payload()

    response = client.post(
        (
            f"/organizations/{organization['id']}"
            "/workflow-templates"
        ),
        json=payload,
    )

    assert response.status_code == 201

    workflow_template = response.json()

    assert workflow_template["organization_id"] == (
        organization["id"]
    )
    assert workflow_template["slug"] == payload["slug"]
    assert workflow_template["name"] == payload["name"]
    assert workflow_template["work_item_label"] == (
        payload["work_item_label"]
    )
    assert workflow_template["work_item_label_plural"] == (
        payload["work_item_label_plural"]
    )
    assert workflow_template["description"] == (
        payload["description"]
    )
    assert workflow_template["status"] == "draft"
    assert workflow_template["created_at"] is not None
    assert workflow_template["updated_at"] is not None


def test_lists_workflow_templates(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids,
    )
    payload = workflow_template_payload()

    create_response = client.post(
        (
            f"/organizations/{organization['id']}"
            "/workflow-templates"
        ),
        json=payload,
    )

    assert create_response.status_code == 201

    created_template = create_response.json()

    response = client.get(
        (
            f"/organizations/{organization['id']}"
            "/workflow-templates"
        )
    )

    assert response.status_code == 200
    assert any(
        workflow_template["id"] == created_template["id"]
        for workflow_template in response.json()
    )


def test_retrieves_workflow_template(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids,
    )

    create_response = client.post(
        (
            f"/organizations/{organization['id']}"
            "/workflow-templates"
        ),
        json=workflow_template_payload(),
    )

    assert create_response.status_code == 201

    created_template = create_response.json()

    response = client.get(
        (
            f"/organizations/{organization['id']}"
            "/workflow-templates/"
            f"{created_template['id']}"
        )
    )

    assert response.status_code == 200
    assert response.json() == created_template


def test_rejects_duplicate_workflow_template_slug(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids,
    )
    payload = workflow_template_payload(
        slug="duplicate-workflow",
    )
    endpoint = (
        f"/organizations/{organization['id']}"
        "/workflow-templates"
    )

    first_response = client.post(
        endpoint,
        json=payload,
    )

    assert first_response.status_code == 201

    duplicate_payload = workflow_template_payload(
        slug=payload["slug"],
    )

    duplicate_response = client.post(
        endpoint,
        json=duplicate_payload,
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": (
            "A workflow template with this slug "
            "already exists in the organization."
        ),
    }


def test_allows_same_template_slug_in_different_organizations(
    created_organization_ids: list[UUID],
) -> None:
    first_organization = create_test_organization(
        created_organization_ids,
    )
    second_organization = create_test_organization(
        created_organization_ids,
    )
    shared_slug = "shared-workflow"

    first_response = client.post(
        (
            f"/organizations/{first_organization['id']}"
            "/workflow-templates"
        ),
        json=workflow_template_payload(
            slug=shared_slug,
        ),
    )
    second_response = client.post(
        (
            f"/organizations/{second_organization['id']}"
            "/workflow-templates"
        ),
        json=workflow_template_payload(
            slug=shared_slug,
        ),
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["organization_id"] != (
        second_response.json()["organization_id"]
    )


def test_returns_404_for_missing_workflow_template(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids,
    )

    response = client.get(
        (
            f"/organizations/{organization['id']}"
            f"/workflow-templates/{uuid4()}"
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workflow template not found.",
    }


def test_returns_404_for_missing_organization() -> None:
    response = client.get(
        f"/organizations/{uuid4()}/workflow-templates"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Organization not found.",
    }