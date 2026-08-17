from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from flowlens.database import SessionLocal
from flowlens.main import app
from flowlens.models import Organization, WorkItem


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
            delete(WorkItem).where(
                WorkItem.organization_id.in_(
                    organization_ids
                ),
            )
        )
        session.execute(
            delete(Organization).where(
                Organization.id.in_(
                    organization_ids
                ),
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


def create_test_user(
    organization_id: str,
) -> dict[str, object]:
    identifier = uuid4().hex[:12]

    response = client.post(
        f"/organizations/{organization_id}/users",
        json={
            "email": (
                f"work-item-owner-{identifier}"
                "@example.com"
            ),
            "display_name": "Work Item Owner",
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
            "slug": f"work-item-template-{identifier}",
            "name": "Work Item Test Workflow",
            "work_item_label": "Launch",
            "work_item_label_plural": "Launches",
            "description": (
                "Workflow used to test work items."
            ),
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_template_version(
    organization_id: str,
    workflow_template_id: str,
) -> dict[str, object]:
    response = client.post(
        (
            f"/organizations/{organization_id}"
            "/workflow-templates/"
            f"{workflow_template_id}/versions"
        ),
        json={
            "change_summary": (
                "Initial work-item test configuration."
            ),
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_stage(
    organization_id: str,
    workflow_template_id: str,
    template_version_id: str,
    *,
    active: bool = True,
    sequence: int = 1,
) -> dict[str, object]:
    identifier = uuid4().hex[:8]

    response = client.post(
        (
            f"/organizations/{organization_id}"
            "/workflow-templates/"
            f"{workflow_template_id}/versions/"
            f"{template_version_id}/stages"
        ),
        json={
            "code": f"intake_{identifier}",
            "name": "Intake",
            "sequence": sequence,
            "description": (
                "Collect initial launch information."
            ),
            "default_owner_role_id": None,
            "sla_minutes": 1440,
            "terminal": False,
            "active": active,
        },
    )

    assert response.status_code == 201

    return response.json()


def publish_test_template_version(
    organization_id: str,
    workflow_template_id: str,
    template_version_id: str,
    publishing_user_id: str,
) -> dict[str, object]:
    response = client.post(
        (
            f"/organizations/{organization_id}"
            "/workflow-templates/"
            f"{workflow_template_id}/versions/"
            f"{template_version_id}/publish"
        ),
        json={
            "published_by_user_id": publishing_user_id,
        },
    )

    assert response.status_code == 200

    return response.json()


def create_published_workflow_configuration(
    created_organization_ids: list[UUID],
) -> dict[str, dict[str, object]]:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    user = create_test_user(organization_id)
    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(
        workflow_template["id"]
    )
    template_version = create_test_template_version(
        organization_id,
        workflow_template_id,
    )
    template_version_id = str(template_version["id"])
    stage = create_test_stage(
        organization_id,
        workflow_template_id,
        template_version_id,
    )

    publish_test_template_version(
        organization_id,
        workflow_template_id,
        template_version_id,
        str(user["id"]),
    )

    return {
        "organization": organization,
        "user": user,
        "workflow_template": workflow_template,
        "template_version": template_version,
        "stage": stage,
    }


def work_item_payload(
    template_version_id: str,
    accountable_owner_id: str,
) -> dict[str, object]:
    return {
        "template_version_id": template_version_id,
        "display_name": "Northstar Customer Launch",
        "accountable_owner_id": accountable_owner_id,
        "target_at": "2026-09-30T17:00:00Z",
    }


def test_creates_work_item(
    created_organization_ids: list[UUID],
) -> None:
    configuration = (
        create_published_workflow_configuration(
            created_organization_ids
        )
    )
    organization_id = str(
        configuration["organization"]["id"]
    )
    template_version_id = str(
        configuration["template_version"]["id"]
    )
    owner_id = str(configuration["user"]["id"])
    stage_id = str(configuration["stage"]["id"])
    payload = work_item_payload(
        template_version_id,
        owner_id,
    )

    response = client.post(
        f"/organizations/{organization_id}/work-items",
        json=payload,
    )

    assert response.status_code == 201

    work_item = response.json()

    assert work_item["organization_id"] == organization_id
    assert (
        work_item["template_version_id"]
        == template_version_id
    )
    assert work_item["display_name"] == payload[
        "display_name"
    ]
    assert work_item["status"] == "active"
    assert (
        work_item["current_stage_definition_id"]
        == stage_id
    )
    assert work_item["risk_status"] == "on_track"
    assert work_item["accountable_owner_id"] == owner_id
    assert work_item["target_at"] == (
        "2026-09-30T17:00:00Z"
    )
    assert work_item["original_target_at"] == (
        "2026-09-30T17:00:00Z"
    )
    assert work_item["paused_at"] is None
    assert work_item["pause_reason"] is None
    assert work_item["completed_at"] is None
    assert work_item["canceled_at"] is None
    assert work_item["cancellation_reason"] is None
    assert work_item["created_at"] is not None
    assert work_item["updated_at"] is not None
    assert work_item["version"] == 1


def test_selects_first_active_stage(
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
    workflow_template_id = str(
        workflow_template["id"]
    )
    template_version = create_test_template_version(
        organization_id,
        workflow_template_id,
    )
    template_version_id = str(template_version["id"])

    create_test_stage(
        organization_id,
        workflow_template_id,
        template_version_id,
        active=False,
        sequence=1,
    )
    expected_stage = create_test_stage(
        organization_id,
        workflow_template_id,
        template_version_id,
        active=True,
        sequence=2,
    )
    create_test_stage(
        organization_id,
        workflow_template_id,
        template_version_id,
        active=True,
        sequence=3,
    )

    publish_test_template_version(
        organization_id,
        workflow_template_id,
        template_version_id,
        str(user["id"]),
    )

    response = client.post(
        f"/organizations/{organization_id}/work-items",
        json=work_item_payload(
            template_version_id,
            str(user["id"]),
        ),
    )

    assert response.status_code == 201
    assert response.json()[
        "current_stage_definition_id"
    ] == str(expected_stage["id"])


def test_lists_and_retrieves_work_item(
    created_organization_ids: list[UUID],
) -> None:
    configuration = (
        create_published_workflow_configuration(
            created_organization_ids
        )
    )
    organization_id = str(
        configuration["organization"]["id"]
    )
    payload = work_item_payload(
        str(configuration["template_version"]["id"]),
        str(configuration["user"]["id"]),
    )

    create_response = client.post(
        f"/organizations/{organization_id}/work-items",
        json=payload,
    )

    assert create_response.status_code == 201

    created_work_item = create_response.json()

    list_response = client.get(
        f"/organizations/{organization_id}/work-items"
    )

    assert list_response.status_code == 200
    assert any(
        work_item["id"] == created_work_item["id"]
        for work_item in list_response.json()
    )

    retrieve_response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/work-items/{created_work_item['id']}"
        )
    )

    assert retrieve_response.status_code == 200
    assert retrieve_response.json() == created_work_item


def test_rejects_draft_template_version(
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
    workflow_template_id = str(
        workflow_template["id"]
    )
    template_version = create_test_template_version(
        organization_id,
        workflow_template_id,
    )
    template_version_id = str(template_version["id"])

    create_test_stage(
        organization_id,
        workflow_template_id,
        template_version_id,
    )

    response = client.post(
        f"/organizations/{organization_id}/work-items",
        json=work_item_payload(
            template_version_id,
            str(user["id"]),
        ),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Work items can only be created from a "
            "published workflow template version."
        ),
    }


def test_rejects_published_version_without_active_stage(
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
    workflow_template_id = str(
        workflow_template["id"]
    )
    template_version = create_test_template_version(
        organization_id,
        workflow_template_id,
    )
    template_version_id = str(template_version["id"])

    create_test_stage(
        organization_id,
        workflow_template_id,
        template_version_id,
        active=False,
    )

    publish_test_template_version(
        organization_id,
        workflow_template_id,
        template_version_id,
        str(user["id"]),
    )

    response = client.post(
        f"/organizations/{organization_id}/work-items",
        json=work_item_payload(
            template_version_id,
            str(user["id"]),
        ),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "The workflow template version must have "
            "an active stage before creating work items."
        ),
    }


def test_rejects_owner_from_another_organization(
    created_organization_ids: list[UUID],
) -> None:
    configuration = (
        create_published_workflow_configuration(
            created_organization_ids
        )
    )
    organization_id = str(
        configuration["organization"]["id"]
    )
    other_organization = create_test_organization(
        created_organization_ids
    )
    other_user = create_test_user(
        str(other_organization["id"])
    )

    response = client.post(
        f"/organizations/{organization_id}/work-items",
        json=work_item_payload(
            str(
                configuration[
                    "template_version"
                ]["id"]
            ),
            str(other_user["id"]),
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Accountable owner not found.",
    }


def test_rejects_template_version_from_another_organization(
    created_organization_ids: list[UUID],
) -> None:
    configuration = (
        create_published_workflow_configuration(
            created_organization_ids
        )
    )
    other_organization = create_test_organization(
        created_organization_ids
    )
    other_organization_id = str(
        other_organization["id"]
    )
    other_user = create_test_user(
        other_organization_id
    )

    response = client.post(
        (
            f"/organizations/{other_organization_id}"
            "/work-items"
        ),
        json=work_item_payload(
            str(
                configuration[
                    "template_version"
                ]["id"]
            ),
            str(other_user["id"]),
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workflow template version not found.",
    }


def test_does_not_retrieve_work_item_from_another_organization(
    created_organization_ids: list[UUID],
) -> None:
    configuration = (
        create_published_workflow_configuration(
            created_organization_ids
        )
    )
    organization_id = str(
        configuration["organization"]["id"]
    )

    create_response = client.post(
        f"/organizations/{organization_id}/work-items",
        json=work_item_payload(
            str(
                configuration[
                    "template_version"
                ]["id"]
            ),
            str(configuration["user"]["id"]),
        ),
    )

    assert create_response.status_code == 201

    other_organization = create_test_organization(
        created_organization_ids
    )

    response = client.get(
        (
            f"/organizations/{other_organization['id']}"
            f"/work-items/{create_response.json()['id']}"
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Work item not found.",
    }


def test_returns_404_for_missing_work_item(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )

    response = client.get(
        (
            f"/organizations/{organization['id']}"
            f"/work-items/{uuid4()}"
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Work item not found.",
    }


def test_returns_404_for_missing_organization() -> None:
    response = client.get(
        f"/organizations/{uuid4()}/work-items"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Organization not found.",
    }