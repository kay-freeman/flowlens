from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from flowlens.schemas import (
    RiskStatus,
    WorkItemCreate,
    WorkItemResponse,
    WorkItemStatus,
)


def valid_work_item_payload() -> dict[str, object]:
    return {
        "template_version_id": str(uuid4()),
        "display_name": "Northstar Customer Launch",
        "accountable_owner_id": str(uuid4()),
        "target_at": "2026-09-30T17:00:00Z",
    }


def test_accepts_valid_work_item_input() -> None:
    payload = valid_work_item_payload()

    work_item = WorkItemCreate.model_validate(payload)

    assert work_item.template_version_id == UUID(
        str(payload["template_version_id"])
    )
    assert work_item.display_name == payload["display_name"]
    assert work_item.accountable_owner_id == UUID(
        str(payload["accountable_owner_id"])
    )
    assert work_item.target_at == datetime(
        2026,
        9,
        30,
        17,
        0,
        tzinfo=UTC,
    )


def test_accepts_work_item_without_target() -> None:
    payload = valid_work_item_payload()
    payload.pop("target_at")

    work_item = WorkItemCreate.model_validate(payload)

    assert work_item.target_at is None


def test_normalizes_work_item_display_name() -> None:
    payload = valid_work_item_payload()
    payload["display_name"] = "  Northstar Customer Launch  "

    work_item = WorkItemCreate.model_validate(payload)

    assert work_item.display_name == "Northstar Customer Launch"


@pytest.mark.parametrize(
    "display_name",
    [
        "",
        " ",
        "   ",
    ],
)
def test_rejects_blank_work_item_display_name(
    display_name: str,
) -> None:
    payload = valid_work_item_payload()
    payload["display_name"] = display_name

    with pytest.raises(ValidationError):
        WorkItemCreate.model_validate(payload)


@pytest.mark.parametrize(
    "status",
    [
        WorkItemStatus.ACTIVE,
        WorkItemStatus.PAUSED,
        WorkItemStatus.COMPLETED,
        WorkItemStatus.CANCELED,
    ],
)
def test_builds_response_with_supported_work_item_status(
    status: WorkItemStatus,
) -> None:
    now = datetime.now(UTC)

    response = WorkItemResponse.model_validate(
        {
            "id": uuid4(),
            "organization_id": uuid4(),
            "template_version_id": uuid4(),
            "display_name": "Northstar Customer Launch",
            "status": status,
            "current_stage_definition_id": uuid4(),
            "risk_status": RiskStatus.ON_TRACK,
            "accountable_owner_id": uuid4(),
            "target_at": now,
            "original_target_at": now,
            "paused_at": None,
            "pause_reason": None,
            "completed_at": None,
            "canceled_at": None,
            "cancellation_reason": None,
            "created_at": now,
            "updated_at": now,
            "version": 1,
        }
    )

    assert response.status == status
    assert response.risk_status == RiskStatus.ON_TRACK
    assert response.version == 1


@pytest.mark.parametrize(
    "risk_status",
    [
        RiskStatus.ON_TRACK,
        RiskStatus.AT_RISK,
        RiskStatus.BLOCKED,
        RiskStatus.PAUSED,
    ],
)
def test_builds_response_with_supported_risk_status(
    risk_status: RiskStatus,
) -> None:
    now = datetime.now(UTC)

    response = WorkItemResponse.model_validate(
        {
            "id": uuid4(),
            "organization_id": uuid4(),
            "template_version_id": uuid4(),
            "display_name": "Northstar Customer Launch",
            "status": WorkItemStatus.ACTIVE,
            "current_stage_definition_id": uuid4(),
            "risk_status": risk_status,
            "accountable_owner_id": uuid4(),
            "target_at": None,
            "original_target_at": None,
            "paused_at": None,
            "pause_reason": None,
            "completed_at": None,
            "canceled_at": None,
            "cancellation_reason": None,
            "created_at": now,
            "updated_at": now,
            "version": 1,
        }
    )

    assert response.risk_status == risk_status


def test_rejects_unsupported_work_item_status() -> None:
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        WorkItemResponse.model_validate(
            {
                "id": uuid4(),
                "organization_id": uuid4(),
                "template_version_id": uuid4(),
                "display_name": "Northstar Customer Launch",
                "status": "pending",
                "current_stage_definition_id": uuid4(),
                "risk_status": RiskStatus.ON_TRACK,
                "accountable_owner_id": uuid4(),
                "target_at": None,
                "original_target_at": None,
                "paused_at": None,
                "pause_reason": None,
                "completed_at": None,
                "canceled_at": None,
                "cancellation_reason": None,
                "created_at": now,
                "updated_at": now,
                "version": 1,
            }
        )


def test_rejects_unsupported_risk_status() -> None:
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        WorkItemResponse.model_validate(
            {
                "id": uuid4(),
                "organization_id": uuid4(),
                "template_version_id": uuid4(),
                "display_name": "Northstar Customer Launch",
                "status": WorkItemStatus.ACTIVE,
                "current_stage_definition_id": uuid4(),
                "risk_status": "unknown",
                "accountable_owner_id": uuid4(),
                "target_at": None,
                "original_target_at": None,
                "paused_at": None,
                "pause_reason": None,
                "completed_at": None,
                "canceled_at": None,
                "cancellation_reason": None,
                "created_at": now,
                "updated_at": now,
                "version": 1,
            }
        )


def test_rejects_nonpositive_work_item_version() -> None:
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        WorkItemResponse.model_validate(
            {
                "id": uuid4(),
                "organization_id": uuid4(),
                "template_version_id": uuid4(),
                "display_name": "Northstar Customer Launch",
                "status": WorkItemStatus.ACTIVE,
                "current_stage_definition_id": uuid4(),
                "risk_status": RiskStatus.ON_TRACK,
                "accountable_owner_id": uuid4(),
                "target_at": None,
                "original_target_at": None,
                "paused_at": None,
                "pause_reason": None,
                "completed_at": None,
                "canceled_at": None,
                "cancellation_reason": None,
                "created_at": now,
                "updated_at": now,
                "version": 0,
            }
        )