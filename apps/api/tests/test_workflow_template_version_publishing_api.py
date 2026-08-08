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
            "name": f"Publishing Test Organization {identifier}",
            "slug": (
                f"publishing-test-organization-{identifier}"
            ),
        },
    )

    assert response.status_code == 201

    organization = response.json()
    created_organization_ids.append(
        UUID(organization["id"])
    )

    return organization


def create_test_user(
    organization_id: str,
) -> dict[str, object]:
    identifier = uuid4().hex[:12]

    response = client.post(
        f"/organizations/{organization_id}/users",
        json={
            "email": (
                f"publisher-{identifier}"
                "@northstar.example"
            ),
            "display_name": "Template Publisher",
            "department": "Operations",
            "identity_source": "demo",
            "external_subject": None,
        },
    )

    assert response.status_code == 201

    return response.json()


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
            "slug": f"publishing-template-{identifier}",
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


def create_test_workflow_template_version(
    organization_id: str,
    workflow_template_id: str,
    change_summary: str,
) -> dict[str, object]:
    response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            "/versions"
        ),
        json={
            "change_summary": change_summary,
        },
    )

    assert response.status_code == 201

    return response.json()


def publish_version(
    organization_id: str,
    workflow_template_id: str,
    workflow_template_version_id: str,
    published_by_user_id: str,
):
    return client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            f"/versions/{workflow_template_version_id}"
            "/publish"
        ),
        json={
            "published_by_user_id": published_by_user_id,
        },
    )


def test_publishes_draft_version_and_activates_template(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    user = create_test_user(organization_id)
    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
        "Initial workflow configuration.",
    )

    response = publish_version(
        organization_id,
        workflow_template_id,
        str(version["id"]),
        str(user["id"]),
    )

    assert response.status_code == 200

    published_version = response.json()

    assert published_version["status"] == "published"
    assert published_version["published_at"] is not None
    assert published_version["published_by_user_id"] == (
        user["id"]
    )

    template_response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
        )
    )

    assert template_response.status_code == 200
    assert template_response.json()["status"] == "active"


def test_publishing_new_version_retires_previous_version(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    user = create_test_user(organization_id)
    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    first_version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
        "Initial workflow configuration.",
    )
    second_version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
        "Add Finance approval requirements.",
    )

    first_publish_response = publish_version(
        organization_id,
        workflow_template_id,
        str(first_version["id"]),
        str(user["id"]),
    )
    second_publish_response = publish_version(
        organization_id,
        workflow_template_id,
        str(second_version["id"]),
        str(user["id"]),
    )

    assert first_publish_response.status_code == 200
    assert second_publish_response.status_code == 200
    assert second_publish_response.json()["status"] == (
        "published"
    )

    first_version_response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            f"/versions/{first_version['id']}"
        )
    )

    assert first_version_response.status_code == 200
    assert first_version_response.json()["status"] == (
        "retired"
    )


def test_rejects_publishing_version_more_than_once(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    user = create_test_user(organization_id)
    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
        "Initial workflow configuration.",
    )

    first_response = publish_version(
        organization_id,
        workflow_template_id,
        str(version["id"]),
        str(user["id"]),
    )
    second_response = publish_version(
        organization_id,
        workflow_template_id,
        str(version["id"]),
        str(user["id"]),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": (
            "Only draft workflow template versions "
            "can be published."
        ),
    }


def test_rejects_publishing_retired_version(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    user = create_test_user(organization_id)
    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    first_version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
        "Initial workflow configuration.",
    )
    second_version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
        "Second workflow configuration.",
    )

    publish_version(
        organization_id,
        workflow_template_id,
        str(first_version["id"]),
        str(user["id"]),
    )
    publish_version(
        organization_id,
        workflow_template_id,
        str(second_version["id"]),
        str(user["id"]),
    )

    response = publish_version(
        organization_id,
        workflow_template_id,
        str(first_version["id"]),
        str(user["id"]),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Only draft workflow template versions "
            "can be published."
        ),
    }


def test_rejects_publisher_from_another_organization(
    created_organization_ids: list[UUID],
) -> None:
    first_organization = create_test_organization(
        created_organization_ids
    )
    second_organization = create_test_organization(
        created_organization_ids
    )

    first_organization_id = str(
        first_organization["id"]
    )
    second_organization_id = str(
        second_organization["id"]
    )

    external_user = create_test_user(
        second_organization_id
    )
    workflow_template = create_test_workflow_template(
        first_organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    version = create_test_workflow_template_version(
        first_organization_id,
        workflow_template_id,
        "Initial workflow configuration.",
    )

    response = publish_version(
        first_organization_id,
        workflow_template_id,
        str(version["id"]),
        str(external_user["id"]),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Publishing user not found.",
    }


def test_returns_404_when_publishing_missing_version(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    user = create_test_user(organization_id)
    workflow_template = create_test_workflow_template(
        organization_id
    )

    response = publish_version(
        organization_id,
        str(workflow_template["id"]),
        str(uuid4()),
        str(user["id"]),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workflow template version not found.",
    }