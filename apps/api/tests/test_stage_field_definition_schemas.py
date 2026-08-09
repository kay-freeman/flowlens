from uuid import uuid4

import pytest
from pydantic import ValidationError

from flowlens.schemas import (
    FieldDefinitionCreate,
    FieldDefinitionResponse,
    FieldType,
    ProvenanceType,
    StageDefinitionCreate,
    StageDefinitionResponse,
)


def stage_definition_payload() -> dict[str, object]:
    return {
        "code": "validation",
        "name": "Validation",
        "sequence": 2,
        "description": (
            "Validate contract, customer, and billing information."
        ),
        "default_owner_role_id": str(uuid4()),
        "sla_minutes": 1440,
        "terminal": False,
        "active": True,
    }


def field_definition_payload() -> dict[str, object]:
    return {
        "key": "contract_value",
        "label": "Contract Value",
        "field_type": "number",
        "required": True,
        "source_type": "external",
        "source_system": "Salesforce",
        "validation_config": {
            "minimum": 0,
        },
        "display_order": 3,
        "sensitive": False,
    }


def test_accepts_valid_stage_definition_input() -> None:
    payload = stage_definition_payload()

    stage = StageDefinitionCreate.model_validate(payload)

    assert stage.code == payload["code"]
    assert stage.name == payload["name"]
    assert stage.sequence == payload["sequence"]
    assert stage.description == payload["description"]
    assert stage.sla_minutes == payload["sla_minutes"]
    assert stage.terminal is False
    assert stage.active is True


def test_normalizes_stage_definition_input() -> None:
    stage = StageDefinitionCreate.model_validate(
        {
            **stage_definition_payload(),
            "code": "  Validation  ",
            "name": "  Validation  ",
            "description": "  Validate launch information.  ",
        }
    )

    assert stage.code == "validation"
    assert stage.name == "Validation"
    assert stage.description == "Validate launch information."


@pytest.mark.parametrize(
    "code",
    [
        "validation-stage",
        "validation stage",
        "_validation",
        "123_validation",
        "validation.stage",
    ],
)
def test_rejects_invalid_stage_codes(code: str) -> None:
    with pytest.raises(ValidationError):
        StageDefinitionCreate.model_validate(
            {
                **stage_definition_payload(),
                "code": code,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "name",
        "description",
    ],
)
def test_rejects_blank_stage_text(field_name: str) -> None:
    with pytest.raises(ValidationError):
        StageDefinitionCreate.model_validate(
            {
                **stage_definition_payload(),
                field_name: "   ",
            }
        )


def test_rejects_nonpositive_stage_sequence() -> None:
    with pytest.raises(ValidationError):
        StageDefinitionCreate.model_validate(
            {
                **stage_definition_payload(),
                "sequence": 0,
            }
        )


def test_rejects_nonpositive_stage_sla() -> None:
    with pytest.raises(ValidationError):
        StageDefinitionCreate.model_validate(
            {
                **stage_definition_payload(),
                "sla_minutes": 0,
            }
        )


def test_builds_stage_definition_response() -> None:
    stage_id = uuid4()
    template_version_id = uuid4()
    role_id = uuid4()

    stage = StageDefinitionResponse.model_validate(
        {
            "id": stage_id,
            "template_version_id": template_version_id,
            "code": "validation",
            "name": "Validation",
            "sequence": 2,
            "description": "Validate launch information.",
            "default_owner_role_id": role_id,
            "sla_minutes": 1440,
            "terminal": False,
            "active": True,
        }
    )

    assert stage.id == stage_id
    assert stage.template_version_id == template_version_id
    assert stage.default_owner_role_id == role_id


def test_accepts_valid_field_definition_input() -> None:
    payload = field_definition_payload()

    field_definition = FieldDefinitionCreate.model_validate(
        payload
    )

    assert field_definition.key == payload["key"]
    assert field_definition.label == payload["label"]
    assert field_definition.field_type == FieldType.NUMBER
    assert field_definition.required is True
    assert (
        field_definition.source_type
        == ProvenanceType.EXTERNAL
    )
    assert (
        field_definition.validation_config
        == payload["validation_config"]
    )
    assert field_definition.display_order == 3
    assert field_definition.sensitive is False


def test_normalizes_field_definition_input() -> None:
    field_definition = FieldDefinitionCreate.model_validate(
        {
            **field_definition_payload(),
            "key": "  Contract_Value  ",
            "label": "  Contract Value  ",
            "source_system": "  Salesforce  ",
        }
    )

    assert field_definition.key == "contract_value"
    assert field_definition.label == "Contract Value"
    assert field_definition.source_system == "Salesforce"


def test_converts_blank_source_system_to_none() -> None:
    field_definition = FieldDefinitionCreate.model_validate(
        {
            **field_definition_payload(),
            "source_system": "   ",
        }
    )

    assert field_definition.source_system is None


@pytest.mark.parametrize(
    "key",
    [
        "contract-value",
        "contract value",
        "_contract_value",
        "123_contract_value",
        "contract.value",
    ],
)
def test_rejects_invalid_field_keys(key: str) -> None:
    with pytest.raises(ValidationError):
        FieldDefinitionCreate.model_validate(
            {
                **field_definition_payload(),
                "key": key,
            }
        )


def test_rejects_blank_field_label() -> None:
    with pytest.raises(ValidationError):
        FieldDefinitionCreate.model_validate(
            {
                **field_definition_payload(),
                "label": "   ",
            }
        )


def test_rejects_nonpositive_display_order() -> None:
    with pytest.raises(ValidationError):
        FieldDefinitionCreate.model_validate(
            {
                **field_definition_payload(),
                "display_order": 0,
            }
        )


@pytest.mark.parametrize(
    "field_type",
    [field_type.value for field_type in FieldType],
)
def test_accepts_supported_field_types(
    field_type: str,
) -> None:
    field_definition = FieldDefinitionCreate.model_validate(
        {
            **field_definition_payload(),
            "field_type": field_type,
        }
    )

    assert field_definition.field_type == field_type


def test_rejects_unsupported_field_type() -> None:
    with pytest.raises(ValidationError):
        FieldDefinitionCreate.model_validate(
            {
                **field_definition_payload(),
                "field_type": "currency",
            }
        )


@pytest.mark.parametrize(
    "source_type",
    [source_type.value for source_type in ProvenanceType],
)
def test_accepts_supported_provenance_types(
    source_type: str,
) -> None:
    field_definition = FieldDefinitionCreate.model_validate(
        {
            **field_definition_payload(),
            "source_type": source_type,
        }
    )

    assert field_definition.source_type == source_type


def test_rejects_unsupported_provenance_type() -> None:
    with pytest.raises(ValidationError):
        FieldDefinitionCreate.model_validate(
            {
                **field_definition_payload(),
                "source_type": "manual",
            }
        )


def test_builds_field_definition_response() -> None:
    field_id = uuid4()
    template_version_id = uuid4()

    field_definition = FieldDefinitionResponse.model_validate(
        {
            "id": field_id,
            "template_version_id": template_version_id,
            "key": "contract_value",
            "label": "Contract Value",
            "field_type": "number",
            "required": True,
            "source_type": "external",
            "source_system": "Salesforce",
            "validation_config": {
                "minimum": 0,
            },
            "display_order": 3,
            "sensitive": False,
        }
    )

    assert field_definition.id == field_id
    assert (
        field_definition.template_version_id
        == template_version_id
    )
    assert field_definition.field_type == FieldType.NUMBER
    assert (
        field_definition.source_type
        == ProvenanceType.EXTERNAL
    )