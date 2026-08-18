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
        UUID(str(organization["id"]))
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
                f"work-item-value-user-{identifier}"
                "@example.com"
            ),
            "display_name": "Work Item Value User",
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
            "slug": f"value-history-{identifier}",
            "name": "Value and History Workflow",
            "work_item_label": "Launch",
            "work_item_label_plural": "Launches",
            "description": (
                "Workflow used to test field values "
                "and stage history."
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
                "Initial value and history configuration."
            ),
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_stage(
    organization_id: str,
    workflow_template_id: str,
    template_version_id: str,
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
            "sequence": 1,
            "description": (
                "Collect initial launch information."
            ),
            "default_owner_role_id": None,
            "sla_minutes": 1440,
            "terminal": False,
            "active": True,
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_field(
    organization_id: str,
    workflow_template_id: str,
    template_version_id: str,
    *,
    key: str,
    label: str,
    field_type: str,
    source_type: str,
    source_system: str | None,
    display_order: int,
) -> dict[str, object]:
    response = client.post(
        (
            f"/organizations/{organization_id}"
            "/workflow-templates/"
            f"{workflow_template_id}/versions/"
            f"{template_version_id}/fields"
        ),
        json={
            "key": key,
            "label": label,
            "field_type": field_type,
            "required": True,
            "source_type": source_type,
            "source_system": source_system,
            "validation_config": None,
            "display_order": display_order,
            "sensitive": False,
        },
    )

    assert response.status_code == 201

    return response.json()


def publish_test_template_version(
    organization_id: str,
    workflow_template_id: str,
    template_version_id: str,
    publishing_user_id: str,
) -> None:
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


def create_test_work_item(
    organization_id: str,
    template_version_id: str,
    accountable_owner_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/organizations/{organization_id}/work-items",
        json={
            "template_version_id": template_version_id,
            "display_name": "Northstar Customer Launch",
            "accountable_owner_id": accountable_owner_id,
            "target_at": "2026-09-30T17:00:00Z",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_published_configuration(
    created_organization_ids: list[UUID],
    *,
    field_type: str = "number",
    source_type: str = "external",
    source_system: str | None = "Salesforce",
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

    field = create_test_field(
        organization_id,
        workflow_template_id,
        template_version_id,
        key="contract_value",
        label="Contract Value",
        field_type=field_type,
        source_type=source_type,
        source_system=source_system,
        display_order=1,
    )

    publish_test_template_version(
        organization_id,
        workflow_template_id,
        template_version_id,
        str(user["id"]),
    )

    work_item = create_test_work_item(
        organization_id,
        template_version_id,
        str(user["id"]),
    )

    return {
        "organization": organization,
        "user": user,
        "workflow_template": workflow_template,
        "template_version": template_version,
        "stage": stage,
        "field": field,
        "work_item": work_item,
    }


def external_field_value_payload(
    field_definition_id: str,
    *,
    value: object = 125000,
) -> dict[str, object]:
    return {
        "field_definition_id": field_definition_id,
        "value": value,
        "provenance_type": "external",
        "source_system": "Salesforce",
        "source_reference": "opportunity-1842",
        "set_by_user_id": None,
    }


def field_values_endpoint(
    organization_id: str,
    work_item_id: str,
) -> str:
    return (
        f"/organizations/{organization_id}"
        f"/work-items/{work_item_id}/field-values"
    )


def test_creates_initial_stage_history(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids
    )

    organization_id = str(
        configuration["organization"]["id"]
    )
    work_item_id = str(
        configuration["work_item"]["id"]
    )

    response = client.get(
        (
            f"/organizations/{organization_id}"
            f"/work-items/{work_item_id}/stage-history"
        )
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["work_item_id"] == work_item_id
    assert history[0]["stage_definition_id"] == str(
        configuration["stage"]["id"]
    )
    assert history[0]["entered_at"] is not None
    assert history[0]["exited_at"] is None
    assert history[0]["entered_by_user_id"] is None
    assert history[0]["actor_source"] == "flowlens"
    assert history[0]["exit_reason"] is None
    assert history[0]["correlation_id"] is not None


def test_sets_external_work_item_field_value(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids
    )

    organization_id = str(
        configuration["organization"]["id"]
    )
    work_item_id = str(
        configuration["work_item"]["id"]
    )
    field_definition_id = str(
        configuration["field"]["id"]
    )

    response = client.put(
        field_values_endpoint(
            organization_id,
            work_item_id,
        ),
        json=external_field_value_payload(
            field_definition_id
        ),
    )

    assert response.status_code == 200

    field_value = response.json()

    assert field_value["work_item_id"] == work_item_id
    assert (
        field_value["field_definition_id"]
        == field_definition_id
    )
    assert field_value["value"] == 125000
    assert field_value["provenance_type"] == "external"
    assert field_value["source_system"] == "Salesforce"
    assert (
        field_value["source_reference"]
        == "opportunity-1842"
    )
    assert field_value["set_by_user_id"] is None
    assert field_value["set_at"] is not None
    assert field_value["updated_at"] is not None


def test_updates_existing_work_item_field_value(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids
    )

    organization_id = str(
        configuration["organization"]["id"]
    )
    work_item_id = str(
        configuration["work_item"]["id"]
    )
    field_definition_id = str(
        configuration["field"]["id"]
    )
    endpoint = field_values_endpoint(
        organization_id,
        work_item_id,
    )

    first_response = client.put(
        endpoint,
        json=external_field_value_payload(
            field_definition_id,
            value=125000,
        ),
    )

    assert first_response.status_code == 200

    updated_payload = external_field_value_payload(
        field_definition_id,
        value=175000,
    )
    updated_payload["source_reference"] = (
        "opportunity-1842-updated"
    )

    update_response = client.put(
        endpoint,
        json=updated_payload,
    )

    assert update_response.status_code == 200
    assert (
        update_response.json()["id"]
        == first_response.json()["id"]
    )
    assert update_response.json()["value"] == 175000
    assert update_response.json()[
        "source_reference"
    ] == "opportunity-1842-updated"

    list_response = client.get(endpoint)

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["value"] == 175000


def test_lists_field_values_in_display_order(
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

    first_field = create_test_field(
        organization_id,
        workflow_template_id,
        template_version_id,
        key="customer_name",
        label="Customer Name",
        field_type="text",
        source_type="user_entered",
        source_system=None,
        display_order=1,
    )
    second_field = create_test_field(
        organization_id,
        workflow_template_id,
        template_version_id,
        key="contract_value",
        label="Contract Value",
        field_type="number",
        source_type="external",
        source_system="Salesforce",
        display_order=2,
    )

    publish_test_template_version(
        organization_id,
        workflow_template_id,
        template_version_id,
        str(user["id"]),
    )

    work_item = create_test_work_item(
        organization_id,
        template_version_id,
        str(user["id"]),
    )
    endpoint = field_values_endpoint(
        organization_id,
        str(work_item["id"]),
    )

    second_response = client.put(
        endpoint,
        json=external_field_value_payload(
            str(second_field["id"])
        ),
    )

    assert second_response.status_code == 200

    first_response = client.put(
        endpoint,
        json={
            "field_definition_id": str(
                first_field["id"]
            ),
            "value": "Northstar",
            "provenance_type": "user_entered",
            "source_system": None,
            "source_reference": None,
            "set_by_user_id": str(user["id"]),
        },
    )

    assert first_response.status_code == 200

    response = client.get(endpoint)

    assert response.status_code == 200
    assert [
        field_value["field_definition_id"]
        for field_value in response.json()
    ] == [
        str(first_field["id"]),
        str(second_field["id"]),
    ]


def test_rejects_field_from_another_template_version(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids
    )

    organization_id = str(
        configuration["organization"]["id"]
    )
    other_template = create_test_workflow_template(
        organization_id
    )
    other_template_id = str(other_template["id"])
    other_version = create_test_template_version(
        organization_id,
        other_template_id,
    )
    other_version_id = str(other_version["id"])

    other_field = create_test_field(
        organization_id,
        other_template_id,
        other_version_id,
        key="other_value",
        label="Other Value",
        field_type="number",
        source_type="external",
        source_system="Salesforce",
        display_order=1,
    )

    response = client.put(
        field_values_endpoint(
            organization_id,
            str(configuration["work_item"]["id"]),
        ),
        json=external_field_value_payload(
            str(other_field["id"])
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Field definition not found.",
    }


def test_rejects_value_that_does_not_match_field_type(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids
    )

    response = client.put(
        field_values_endpoint(
            str(configuration["organization"]["id"]),
            str(configuration["work_item"]["id"]),
        ),
        json=external_field_value_payload(
            str(configuration["field"]["id"]),
            value="not-a-number",
        ),
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "The value does not match the configured "
            "field type."
        ),
    }


def test_rejects_mismatched_provenance_type(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids
    )

    response = client.put(
        field_values_endpoint(
            str(configuration["organization"]["id"]),
            str(configuration["work_item"]["id"]),
        ),
        json={
            "field_definition_id": str(
                configuration["field"]["id"]
            ),
            "value": 125000,
            "provenance_type": "user_entered",
            "source_system": None,
            "source_reference": None,
            "set_by_user_id": str(
                configuration["user"]["id"]
            ),
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "The provenance type does not match the "
            "field definition source type."
        ),
    }


def test_rejects_external_value_without_source_system(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids
    )
    payload = external_field_value_payload(
        str(configuration["field"]["id"])
    )
    payload["source_system"] = None

    response = client.put(
        field_values_endpoint(
            str(configuration["organization"]["id"]),
            str(configuration["work_item"]["id"]),
        ),
        json=payload,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "External field values require a "
            "source system."
        ),
    }


def test_rejects_user_entered_value_without_setting_user(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids,
        field_type="text",
        source_type="user_entered",
        source_system=None,
    )

    response = client.put(
        field_values_endpoint(
            str(configuration["organization"]["id"]),
            str(configuration["work_item"]["id"]),
        ),
        json={
            "field_definition_id": str(
                configuration["field"]["id"]
            ),
            "value": "Northstar",
            "provenance_type": "user_entered",
            "source_system": None,
            "source_reference": None,
            "set_by_user_id": None,
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "User-entered field values require a "
            "setting user."
        ),
    }


def test_rejects_setting_user_from_another_organization(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids,
        field_type="text",
        source_type="user_entered",
        source_system=None,
    )

    other_organization = create_test_organization(
        created_organization_ids
    )
    other_user = create_test_user(
        str(other_organization["id"])
    )

    response = client.put(
        field_values_endpoint(
            str(configuration["organization"]["id"]),
            str(configuration["work_item"]["id"]),
        ),
        json={
            "field_definition_id": str(
                configuration["field"]["id"]
            ),
            "value": "Northstar",
            "provenance_type": "user_entered",
            "source_system": None,
            "source_reference": None,
            "set_by_user_id": str(other_user["id"]),
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Setting user not found.",
    }


def test_does_not_list_data_through_another_organization(
    created_organization_ids: list[UUID],
) -> None:
    configuration = create_published_configuration(
        created_organization_ids
    )
    other_organization = create_test_organization(
        created_organization_ids
    )

    response = client.get(
        field_values_endpoint(
            str(other_organization["id"]),
            str(configuration["work_item"]["id"]),
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Work item not found.",
    }