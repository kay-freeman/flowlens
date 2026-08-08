from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from flowlens.schemas import (
    TemplateStatus,
    WorkflowTemplateCreate,
    WorkflowTemplateResponse,
)


def valid_template_data() -> dict[str, object]:
    return {
        "slug": "contract-to-launch",
        "name": "Contract-to-Launch",
        "work_item_label": "Launch",
        "work_item_label_plural": "Launches",
        "description": (
            "Coordinates work from signed contract "
            "through customer launch."
        ),
    }


def test_accepts_valid_workflow_template_input() -> None:
    template = WorkflowTemplateCreate(
        **valid_template_data(),
    )

    assert template.slug == "contract-to-launch"
    assert template.name == "Contract-to-Launch"
    assert template.work_item_label == "Launch"
    assert template.work_item_label_plural == "Launches"


def test_normalizes_workflow_template_input() -> None:
    template = WorkflowTemplateCreate(
        slug=" Contract-To-Launch ",
        name=" Contract-to-Launch ",
        work_item_label=" Launch ",
        work_item_label_plural=" Launches ",
        description=" Coordinates the launch workflow. ",
    )

    assert template.slug == "contract-to-launch"
    assert template.name == "Contract-to-Launch"
    assert template.work_item_label == "Launch"
    assert template.work_item_label_plural == "Launches"
    assert template.description == (
        "Coordinates the launch workflow."
    )


@pytest.mark.parametrize(
    "slug",
    [
        "contract_to_launch",
        "contract to launch",
        "-contract-to-launch",
        "contract-to-launch-",
        "contract--to-launch",
        "contract.to.launch",
    ],
)
def test_rejects_invalid_workflow_template_slugs(
    slug: str,
) -> None:
    template_data = valid_template_data()
    template_data["slug"] = slug

    with pytest.raises(ValidationError):
        WorkflowTemplateCreate(**template_data)


@pytest.mark.parametrize(
    "field_name",
    [
        "name",
        "work_item_label",
        "work_item_label_plural",
        "description",
    ],
)
def test_rejects_blank_required_text(
    field_name: str,
) -> None:
    template_data = valid_template_data()
    template_data[field_name] = "   "

    with pytest.raises(ValidationError):
        WorkflowTemplateCreate(**template_data)


def test_builds_workflow_template_response() -> None:
    template_id = uuid4()
    organization_id = uuid4()
    timestamp = datetime.now(UTC)

    response = WorkflowTemplateResponse(
        id=template_id,
        organization_id=organization_id,
        slug="contract-to-launch",
        name="Contract-to-Launch",
        work_item_label="Launch",
        work_item_label_plural="Launches",
        description="Coordinates the launch workflow.",
        status=TemplateStatus.DRAFT,
        created_at=timestamp,
        updated_at=timestamp,
    )

    assert response.id == template_id
    assert response.organization_id == organization_id
    assert response.status is TemplateStatus.DRAFT
    assert response.created_at == timestamp
    assert response.updated_at == timestamp


@pytest.mark.parametrize(
    "status",
    [
        TemplateStatus.DRAFT,
        TemplateStatus.ACTIVE,
        TemplateStatus.ARCHIVED,
    ],
)
def test_accepts_supported_template_statuses(
    status: TemplateStatus,
) -> None:
    timestamp = datetime.now(UTC)

    response = WorkflowTemplateResponse(
        id=uuid4(),
        organization_id=uuid4(),
        slug="contract-to-launch",
        name="Contract-to-Launch",
        work_item_label="Launch",
        work_item_label_plural="Launches",
        description="Coordinates the launch workflow.",
        status=status,
        created_at=timestamp,
        updated_at=timestamp,
    )

    assert response.status is status


def test_rejects_unsupported_template_status() -> None:
    timestamp = datetime.now(UTC)

    with pytest.raises(ValidationError):
        WorkflowTemplateResponse(
            id=uuid4(),
            organization_id=uuid4(),
            slug="contract-to-launch",
            name="Contract-to-Launch",
            work_item_label="Launch",
            work_item_label_plural="Launches",
            description="Coordinates the launch workflow.",
            status="published",
            created_at=timestamp,
            updated_at=timestamp,
        )