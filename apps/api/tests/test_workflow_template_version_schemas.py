from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from flowlens.schemas import (
    VersionStatus,
    WorkflowTemplateVersionCreate,
    WorkflowTemplateVersionResponse,
)


def test_accepts_valid_workflow_template_version_input() -> None:
    version = WorkflowTemplateVersionCreate(
        change_summary=(
            "Initial contract-to-launch workflow configuration."
        ),
    )

    assert version.change_summary == (
        "Initial contract-to-launch workflow configuration."
    )


def test_normalizes_workflow_template_version_input() -> None:
    version = WorkflowTemplateVersionCreate(
        change_summary="  Initial workflow configuration.  ",
    )

    assert version.change_summary == "Initial workflow configuration."


@pytest.mark.parametrize(
    "change_summary",
    [
        "",
        " ",
        "   ",
    ],
)
def test_rejects_blank_change_summary(
    change_summary: str,
) -> None:
    with pytest.raises(ValidationError):
        WorkflowTemplateVersionCreate(
            change_summary=change_summary,
        )


@pytest.mark.parametrize(
    "status",
    [
        VersionStatus.DRAFT,
        VersionStatus.PUBLISHED,
        VersionStatus.RETIRED,
    ],
)
def test_builds_workflow_template_version_response(
    status: VersionStatus,
) -> None:
    version_id = uuid4()
    workflow_template_id = uuid4()
    published_by_user_id = uuid4()
    created_at = datetime.now(UTC)

    published_at = (
        created_at
        if status is VersionStatus.PUBLISHED
        else None
    )
    publisher_id = (
        published_by_user_id
        if status is VersionStatus.PUBLISHED
        else None
    )

    response = WorkflowTemplateVersionResponse(
        id=version_id,
        workflow_template_id=workflow_template_id,
        version_number=1,
        status=status,
        change_summary="Initial workflow configuration.",
        published_at=published_at,
        published_by_user_id=publisher_id,
        created_at=created_at,
    )

    assert response.id == version_id
    assert response.workflow_template_id == workflow_template_id
    assert response.version_number == 1
    assert response.status is status
    assert response.change_summary == (
        "Initial workflow configuration."
    )
    assert response.published_at == published_at
    assert response.published_by_user_id == publisher_id
    assert response.created_at == created_at


def test_rejects_unsupported_version_status() -> None:
    with pytest.raises(ValidationError):
        WorkflowTemplateVersionResponse(
            id=uuid4(),
            workflow_template_id=uuid4(),
            version_number=1,
            status="active",
            change_summary="Initial workflow configuration.",
            published_at=None,
            published_by_user_id=None,
            created_at=datetime.now(UTC),
        )


def test_rejects_nonpositive_version_number() -> None:
    with pytest.raises(ValidationError):
        WorkflowTemplateVersionResponse(
            id=uuid4(),
            workflow_template_id=uuid4(),
            version_number=0,
            status=VersionStatus.DRAFT,
            change_summary="Initial workflow configuration.",
            published_at=None,
            published_by_user_id=None,
            created_at=datetime.now(UTC),
        )