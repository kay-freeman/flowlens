from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from flowlens.models import (
    FieldDefinition,
    StageDefinition,
)
from flowlens.schemas import (
    FieldDefinitionCreate,
    StageDefinitionCreate,
)


def create_stage_definition(
    session: Session,
    template_version_id: UUID,
    stage_data: StageDefinitionCreate,
) -> StageDefinition:
    stage_definition = StageDefinition(
        template_version_id=template_version_id,
        code=stage_data.code,
        name=stage_data.name,
        sequence=stage_data.sequence,
        description=stage_data.description,
        default_owner_role_id=(
            stage_data.default_owner_role_id
        ),
        sla_minutes=stage_data.sla_minutes,
        terminal=stage_data.terminal,
        active=stage_data.active,
    )

    session.add(stage_definition)
    session.commit()
    session.refresh(stage_definition)

    return stage_definition


def list_stage_definitions(
    session: Session,
    template_version_id: UUID,
) -> list[StageDefinition]:
    statement = (
        select(StageDefinition)
        .where(
            StageDefinition.template_version_id
            == template_version_id,
        )
        .order_by(
            StageDefinition.sequence,
            StageDefinition.code,
        )
    )

    return list(session.scalars(statement).all())


def get_stage_definition(
    session: Session,
    template_version_id: UUID,
    stage_definition_id: UUID,
) -> StageDefinition | None:
    statement = select(StageDefinition).where(
        StageDefinition.template_version_id
        == template_version_id,
        StageDefinition.id == stage_definition_id,
    )

    return session.scalar(statement)


def get_stage_definition_by_code(
    session: Session,
    template_version_id: UUID,
    code: str,
) -> StageDefinition | None:
    statement = select(StageDefinition).where(
        StageDefinition.template_version_id
        == template_version_id,
        StageDefinition.code == code,
    )

    return session.scalar(statement)


def create_field_definition(
    session: Session,
    template_version_id: UUID,
    field_data: FieldDefinitionCreate,
) -> FieldDefinition:
    field_definition = FieldDefinition(
        template_version_id=template_version_id,
        key=field_data.key,
        label=field_data.label,
        field_type=field_data.field_type.value,
        required=field_data.required,
        source_type=field_data.source_type.value,
        source_system=field_data.source_system,
        validation_config=field_data.validation_config,
        display_order=field_data.display_order,
        sensitive=field_data.sensitive,
    )

    session.add(field_definition)
    session.commit()
    session.refresh(field_definition)

    return field_definition


def list_field_definitions(
    session: Session,
    template_version_id: UUID,
) -> list[FieldDefinition]:
    statement = (
        select(FieldDefinition)
        .where(
            FieldDefinition.template_version_id
            == template_version_id,
        )
        .order_by(
            FieldDefinition.display_order,
            FieldDefinition.key,
        )
    )

    return list(session.scalars(statement).all())


def get_field_definition(
    session: Session,
    template_version_id: UUID,
    field_definition_id: UUID,
) -> FieldDefinition | None:
    statement = select(FieldDefinition).where(
        FieldDefinition.template_version_id
        == template_version_id,
        FieldDefinition.id == field_definition_id,
    )

    return session.scalar(statement)


def get_field_definition_by_key(
    session: Session,
    template_version_id: UUID,
    key: str,
) -> FieldDefinition | None:
    statement = select(FieldDefinition).where(
        FieldDefinition.template_version_id
        == template_version_id,
        FieldDefinition.key == key,
    )

    return session.scalar(statement)