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


def create_test_organization(
    created_organization_ids: list[UUID],
) -> dict[str, object]:
    identifier = uuid4().hex[:12]

    response = client.post(
        "/organizations",
        json={
            "name": f"Version Test Organization {identifier}",
            "slug": f"version-test-organization-{identifier}",
        },
    )

    assert response.status_code == 201

    organization = response.json()
    created_organization_ids.append(
        UUID(organization["id"])
    )

    return organization


def create_test_workflow_template(
    organization_id: str,
) -> dict[str, object]:
    identifier = uuid4().hex[:12]

    response = client.post(
        (
            f"/organizations/{organization_id}"
            "/workflow-templates"
        ),
        json={
            "slug": f"contract-to-launch-{identifier}",
            "name": "Contract-to-Launch",
            "work_item_label": "Launch",
            "work_item_label_plural": "Launches",
            "description": (
                "Coordinates work from signed contract "
                "through customer launch."
            ),
        },
    )

    assert response.status_code == 201

    return response.json()


def version_payload(
    summary: str = "Initial workflow configuration.",
) -> dict[str, str]:
    return {
        "change_summary": summary,
    }


def test_creates_first_workflow_template_version(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            "/versions"
        ),
        json=version_payload(),
    )

    assert response.status_code == 201

    version = response.json()

    assert version["workflow_template_id"] == (
        workflow_template_id
    )
    assert version["version_number"] == 1
    assert version["status"] == "draft"
    assert version["change_summary"] == (
        "Initial workflow configuration."
    )
    assert version["published_at"] is None
    assert version["published_by_user_id"] is None
    assert version["created_at"] is not None


def test_assigns_sequential_version_numbers(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    first_response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            "/versions"
        ),
        json=version_payload("Initial version."),
    )
    second_response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            "/versions"
        ),
        json=version_payload("Second version."),
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["version_number"] == 1
    assert second_response.json()["version_number"] == 2


def test_lists_workflow_template_versions_in_order(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    for summary in [
        "Initial version.",
        "Second version.",
        "Third version.",
    ]:
        response = client.post(
            (
                f"/organizations/{organization_id}"
                f"/workflow-templates/{workflow_template_id}"
                "/versions"
            ),
            json=version_payload(summary),
        )

        assert response.status_code == 201

    response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            "/versions"
        )
    )

    assert response.status_code == 200

    versions = response.json()

    assert [
        version["version_number"]
        for version in versions
    ] == [1, 2, 3]


def test_retrieves_workflow_template_version(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    create_response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            "/versions"
        ),
        json=version_payload(),
    )

    version = create_response.json()

    response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            f"/versions/{version['id']}"
        )
    )

    assert response.status_code == 200
    assert response.json() == version


def test_does_not_return_version_from_another_template(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    first_template = create_test_workflow_template(
        organization_id
    )
    second_template = create_test_workflow_template(
        organization_id
    )

    create_response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{first_template['id']}"
            "/versions"
        ),
        json=version_payload(),
    )

    version_id = create_response.json()["id"]

    response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{second_template['id']}"
            f"/versions/{version_id}"
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workflow template version not found.",
    }


def test_returns_404_for_missing_workflow_template_version(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    workflow_template = create_test_workflow_template(
        organization_id
    )

    response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template['id']}"
            f"/versions/{uuid4()}"
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workflow template version not found.",
    }


def test_returns_404_for_missing_workflow_template(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{uuid4()}"
            "/versions"
        ),
        json=version_payload(),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workflow template not found.",
    }


def test_returns_404_for_missing_organization() -> None:
    response = client.post(
        (
            f"/organizations/{uuid4()}"
            f"/workflow-templates/{uuid4()}"
            "/versions"
        ),
        json=version_payload(),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Organization not found.",
    }