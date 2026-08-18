from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from flowlens.schemas import (
    ActorSource,
    ProvenanceType,
    StageHistoryResponse,
    WorkItemFieldValueResponse,
    WorkItemFieldValueSet,
)


def valid_field_value_payload() -> dict[str, object]:
    return {
        "field_definition_id": uuid4(),
        "value": {
            "amount": 125000,
            "currency": "USD",
        },
        "provenance_type": ProvenanceType.EXTERNAL,
        "source_system": "Salesforce",
        "source_reference": "opportunity-1842",
        "set_by_user_id": None,
    }


def test_accepts_valid_work_item_field_value_input() -> None:
    payload = valid_field_value_payload()

    field_value = WorkItemFieldValueSet.model_validate(
        payload
    )

    assert field_value.field_definition_id == payload[
        "field_definition_id"
    ]
    assert field_value.value == payload["value"]
    assert (
        field_value.provenance_type
        == ProvenanceType.EXTERNAL
    )
    assert field_value.source_system == "Salesforce"
    assert (
        field_value.source_reference
        == "opportunity-1842"
    )
    assert field_value.set_by_user_id is None


def test_normalizes_optional_source_text() -> None:
    payload = valid_field_value_payload()
    payload["source_system"] = "  Salesforce  "
    payload["source_reference"] = "  opportunity-1842  "

    field_value = WorkItemFieldValueSet.model_validate(
        payload
    )

    assert field_value.source_system == "Salesforce"
    assert (
        field_value.source_reference
        == "opportunity-1842"
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "source_system",
        "source_reference",
    ],
)
def test_converts_blank_source_text_to_none(
    field_name: str,
) -> None:
    payload = valid_field_value_payload()
    payload[field_name] = "   "

    field_value = WorkItemFieldValueSet.model_validate(
        payload
    )

    assert getattr(field_value, field_name) is None


@pytest.mark.parametrize(
    "value",
    [
        "Northstar",
        125000,
        12.5,
        True,
        ["legal", "finance"],
        {"amount": 125000},
    ],
)
def test_accepts_supported_json_value_shapes(
    value: object,
) -> None:
    payload = valid_field_value_payload()
    payload["value"] = value

    field_value = WorkItemFieldValueSet.model_validate(
        payload
    )

    assert field_value.value == value


@pytest.mark.parametrize(
    "provenance_type",
    [
        ProvenanceType.EXTERNAL,
        ProvenanceType.USER_ENTERED,
        ProvenanceType.CALCULATED,
        ProvenanceType.DERIVED,
        ProvenanceType.IMPORTED,
    ],
)
def test_accepts_supported_provenance_types(
    provenance_type: ProvenanceType,
) -> None:
    payload = valid_field_value_payload()
    payload["provenance_type"] = provenance_type

    field_value = WorkItemFieldValueSet.model_validate(
        payload
    )

    assert field_value.provenance_type == provenance_type


def test_rejects_unsupported_provenance_type() -> None:
    payload = valid_field_value_payload()
    payload["provenance_type"] = "manual"

    with pytest.raises(ValidationError):
        WorkItemFieldValueSet.model_validate(payload)


def test_rejects_missing_field_value() -> None:
    payload = valid_field_value_payload()
    payload.pop("value")

    with pytest.raises(ValidationError):
        WorkItemFieldValueSet.model_validate(payload)


def test_builds_work_item_field_value_response() -> None:
    now = datetime.now(UTC)
    work_item_id = uuid4()
    field_definition_id = uuid4()

    response = WorkItemFieldValueResponse.model_validate(
        {
            "id": uuid4(),
            "work_item_id": work_item_id,
            "field_definition_id": field_definition_id,
            "value": 125000,
            "provenance_type": (
                ProvenanceType.USER_ENTERED
            ),
            "source_system": None,
            "source_reference": None,
            "set_by_user_id": uuid4(),
            "set_at": now,
            "updated_at": now,
        }
    )

    assert response.work_item_id == work_item_id
    assert (
        response.field_definition_id
        == field_definition_id
    )
    assert response.value == 125000
    assert (
        response.provenance_type
        == ProvenanceType.USER_ENTERED
    )


@pytest.mark.parametrize(
    "actor_source",
    [
        ActorSource.USER,
        ActorSource.FLOWLENS,
        ActorSource.EXTERNAL_SYSTEM,
        ActorSource.IMPORT,
    ],
)
def test_builds_stage_history_with_supported_actor_source(
    actor_source: ActorSource,
) -> None:
    now = datetime.now(UTC)
    work_item_id = uuid4()
    stage_definition_id = uuid4()
    correlation_id = uuid4()

    response = StageHistoryResponse.model_validate(
        {
            "id": uuid4(),
            "work_item_id": work_item_id,
            "stage_definition_id": stage_definition_id,
            "entered_at": now,
            "exited_at": None,
            "entered_by_user_id": None,
            "actor_source": actor_source,
            "exit_reason": None,
            "correlation_id": correlation_id,
        }
    )

    assert response.work_item_id == work_item_id
    assert (
        response.stage_definition_id
        == stage_definition_id
    )
    assert response.actor_source == actor_source
    assert response.exited_at is None
    assert response.correlation_id == correlation_id


def test_rejects_unsupported_actor_source() -> None:
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        StageHistoryResponse.model_validate(
            {
                "id": uuid4(),
                "work_item_id": uuid4(),
                "stage_definition_id": uuid4(),
                "entered_at": now,
                "exited_at": None,
                "entered_by_user_id": None,
                "actor_source": "automation",
                "exit_reason": None,
                "correlation_id": uuid4(),
            }
        )