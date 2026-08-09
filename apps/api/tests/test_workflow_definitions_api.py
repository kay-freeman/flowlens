from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from flowlens.database import SessionLocal
from flowlens.main import app
from flowlens.models import (
    Organization,
    WorkflowTemplateVersion,
)


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
            "name": f"Definition Test {identifier}",
            "slug": f"definition-test-{identifier}",
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
            "slug": f"definition-workflow-{identifier}",
            "name": f"Definition Workflow {identifier}",
            "work_item_label": "Launch",
            "work_item_label_plural": "Launches",
            "description": (
                "Workflow used to test configurable definitions."
            ),
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_workflow_template_version(
    organization_id: str,
    workflow_template_id: str,
) -> dict[str, object]:
    response = client.post(
        (
            f"/organizations/{organization_id}"
            f"/workflow-templates/{workflow_template_id}"
            "/versions"
        ),
        json={
            "change_summary": (
                "Initial configurable workflow definitions."
            ),
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_role(
    organization_id: str,
) -> dict[str, object]:
    identifier = uuid4().hex[:12]

    response = client.post(
        f"/organizations/{organization_id}/roles",
        json={
            "code": f"definition_owner_{identifier}",
            "name": f"Definition Owner {identifier}",
            "description": (
                "Owns work in a configured workflow stage."
            ),
            "permissions": [
                "work_items:read",
                "work_items:update",
            ],
        },
    )

    assert response.status_code == 201

    return response.json()


def stage_payload(
    *,
    code: str = "validation",
    sequence: int = 2,
    default_owner_role_id: str | None = None,
) -> dict[str, object]:
    return {
        "code": code,
        "name": code.replace("_", " ").title(),
        "sequence": sequence,
        "description": f"Configured {code} workflow stage.",
        "default_owner_role_id": default_owner_role_id,
        "sla_minutes": 1440,
        "terminal": False,
        "active": True,
    }


def field_payload(
    *,
    key: str = "contract_value",
    display_order: int = 2,
) -> dict[str, object]:
    return {
        "key": key,
        "label": key.replace("_", " ").title(),
        "field_type": "number",
        "required": True,
        "source_type": "external",
        "source_system": "Salesforce",
        "validation_config": {
            "minimum": 0,
        },
        "display_order": display_order,
        "sensitive": False,
    }


def version_endpoint(
    organization_id: str,
    workflow_template_id: str,
    workflow_template_version_id: str,
) -> str:
    return (
        f"/organizations/{organization_id}"
        f"/workflow-templates/{workflow_template_id}"
        f"/versions/{workflow_template_version_id}"
    )


def set_version_status(
    workflow_template_version_id: str,
    version_status: str,
) -> None:
    with SessionLocal() as session:
        workflow_template_version = session.get(
            WorkflowTemplateVersion,
            UUID(workflow_template_version_id),
        )

        assert workflow_template_version is not None

        workflow_template_version.status = version_status
        session.commit()


def create_test_context(
    created_organization_ids: list[UUID],
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    organization = create_test_organization(
        created_organization_ids
    )
    organization_id = str(organization["id"])

    workflow_template = create_test_workflow_template(
        organization_id
    )
    workflow_template_id = str(workflow_template["id"])

    workflow_template_version = (
        create_test_workflow_template_version(
            organization_id,
            workflow_template_id,
        )
    )

    return (
        organization,
        workflow_template,
        workflow_template_version,
    )


def test_creates_stage_definition(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    organization_id = str(organization["id"])
    role = create_test_role(organization_id)
    payload = stage_payload(
        default_owner_role_id=str(role["id"]),
    )
    endpoint = version_endpoint(
        organization_id,
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    response = client.post(
        f"{endpoint}/stages",
        json=payload,
    )

    assert response.status_code == 201

    stage = response.json()

    assert (
        stage["template_version_id"]
        == workflow_template_version["id"]
    )
    assert stage["code"] == payload["code"]
    assert stage["sequence"] == payload["sequence"]
    assert (
        stage["default_owner_role_id"]
        == role["id"]
    )
    assert stage["terminal"] is False
    assert stage["active"] is True


def test_lists_stage_definitions_in_sequence_order(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    second_response = client.post(
        f"{endpoint}/stages",
        json=stage_payload(
            code="validation",
            sequence=2,
        ),
    )
    first_response = client.post(
        f"{endpoint}/stages",
        json=stage_payload(
            code="intake",
            sequence=1,
        ),
    )

    assert second_response.status_code == 201
    assert first_response.status_code == 201

    response = client.get(f"{endpoint}/stages")

    assert response.status_code == 200
    assert [
        stage["code"]
        for stage in response.json()
    ] == [
        "intake",
        "validation",
    ]


def test_retrieves_stage_definition(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    create_response = client.post(
        f"{endpoint}/stages",
        json=stage_payload(),
    )

    assert create_response.status_code == 201

    created_stage = create_response.json()

    response = client.get(
        f"{endpoint}/stages/{created_stage['id']}"
    )

    assert response.status_code == 200
    assert response.json() == created_stage


def test_rejects_duplicate_stage_code(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )
    payload = stage_payload()

    first_response = client.post(
        f"{endpoint}/stages",
        json=payload,
    )
    duplicate_response = client.post(
        f"{endpoint}/stages",
        json=payload,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": (
            "A stage definition with this code already "
            "exists in the workflow template version."
        ),
    }


def test_rejects_stage_owner_role_from_another_organization(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    other_organization = create_test_organization(
        created_organization_ids
    )
    other_role = create_test_role(
        str(other_organization["id"])
    )

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    response = client.post(
        f"{endpoint}/stages",
        json=stage_payload(
            default_owner_role_id=str(other_role["id"]),
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Default owner role not found.",
    }


@pytest.mark.parametrize(
    "version_status",
    [
        "published",
        "retired",
    ],
)
def test_rejects_stage_creation_on_nondraft_version(
    created_organization_ids: list[UUID],
    version_status: str,
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    set_version_status(
        str(workflow_template_version["id"]),
        version_status,
    )

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    response = client.post(
        f"{endpoint}/stages",
        json=stage_payload(),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Definitions can only be changed on draft "
            "workflow template versions."
        ),
    }


def test_does_not_return_stage_from_another_version(
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

    first_version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
    )
    second_version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
    )

    first_endpoint = version_endpoint(
        organization_id,
        workflow_template_id,
        str(first_version["id"]),
    )
    second_endpoint = version_endpoint(
        organization_id,
        workflow_template_id,
        str(second_version["id"]),
    )

    create_response = client.post(
        f"{first_endpoint}/stages",
        json=stage_payload(),
    )

    assert create_response.status_code == 201

    response = client.get(
        (
            f"{second_endpoint}/stages/"
            f"{create_response.json()['id']}"
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Stage definition not found.",
    }


def test_creates_field_definition(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    payload = field_payload()
    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    response = client.post(
        f"{endpoint}/fields",
        json=payload,
    )

    assert response.status_code == 201

    field_definition = response.json()

    assert (
        field_definition["template_version_id"]
        == workflow_template_version["id"]
    )
    assert field_definition["key"] == payload["key"]
    assert (
        field_definition["field_type"]
        == payload["field_type"]
    )
    assert (
        field_definition["source_type"]
        == payload["source_type"]
    )
    assert (
        field_definition["validation_config"]
        == payload["validation_config"]
    )


def test_lists_field_definitions_in_display_order(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    second_response = client.post(
        f"{endpoint}/fields",
        json=field_payload(
            key="contract_value",
            display_order=2,
        ),
    )
    first_response = client.post(
        f"{endpoint}/fields",
        json=field_payload(
            key="customer_name",
            display_order=1,
        ),
    )

    assert second_response.status_code == 201
    assert first_response.status_code == 201

    response = client.get(f"{endpoint}/fields")

    assert response.status_code == 200
    assert [
        field_definition["key"]
        for field_definition in response.json()
    ] == [
        "customer_name",
        "contract_value",
    ]


def test_retrieves_field_definition(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    create_response = client.post(
        f"{endpoint}/fields",
        json=field_payload(),
    )

    assert create_response.status_code == 201

    created_field = create_response.json()

    response = client.get(
        f"{endpoint}/fields/{created_field['id']}"
    )

    assert response.status_code == 200
    assert response.json() == created_field


def test_rejects_duplicate_field_key(
    created_organization_ids: list[UUID],
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )
    payload = field_payload()

    first_response = client.post(
        f"{endpoint}/fields",
        json=payload,
    )
    duplicate_response = client.post(
        f"{endpoint}/fields",
        json=payload,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": (
            "A field definition with this key already "
            "exists in the workflow template version."
        ),
    }


@pytest.mark.parametrize(
    "version_status",
    [
        "published",
        "retired",
    ],
)
def test_rejects_field_creation_on_nondraft_version(
    created_organization_ids: list[UUID],
    version_status: str,
) -> None:
    (
        organization,
        workflow_template,
        workflow_template_version,
    ) = create_test_context(created_organization_ids)

    set_version_status(
        str(workflow_template_version["id"]),
        version_status,
    )

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(workflow_template_version["id"]),
    )

    response = client.post(
        f"{endpoint}/fields",
        json=field_payload(),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Definitions can only be changed on draft "
            "workflow template versions."
        ),
    }


def test_does_not_return_field_from_another_version(
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

    first_version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
    )
    second_version = create_test_workflow_template_version(
        organization_id,
        workflow_template_id,
    )

    first_endpoint = version_endpoint(
        organization_id,
        workflow_template_id,
        str(first_version["id"]),
    )
    second_endpoint = version_endpoint(
        organization_id,
        workflow_template_id,
        str(second_version["id"]),
    )

    create_response = client.post(
        f"{first_endpoint}/fields",
        json=field_payload(),
    )

    assert create_response.status_code == 201

    response = client.get(
        (
            f"{second_endpoint}/fields/"
            f"{create_response.json()['id']}"
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Field definition not found.",
    }


def test_returns_404_for_missing_workflow_template_version(
    created_organization_ids: list[UUID],
) -> None:
    organization = create_test_organization(
        created_organization_ids
    )
    workflow_template = create_test_workflow_template(
        str(organization["id"])
    )

    endpoint = version_endpoint(
        str(organization["id"]),
        str(workflow_template["id"]),
        str(uuid4()),
    )

    stage_response = client.get(f"{endpoint}/stages")
    field_response = client.get(f"{endpoint}/fields")

    assert stage_response.status_code == 404
    assert stage_response.json() == {
        "detail": "Workflow template version not found.",
    }
    assert field_response.status_code == 404
    assert field_response.json() == {
        "detail": "Workflow template version not found.",
    }