from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from flowlens.models import (
    FieldDefinition,
    StageDefinition,
    StageHistory,
    WorkItem,
    WorkItemFieldValue,
    WorkflowTemplate,
    WorkflowTemplateVersion,
)
from flowlens.schemas import (
    WorkItemCreate,
    WorkItemFieldValueSet,
)


def get_workflow_template_version_for_organization(
    session: Session,
    organization_id: UUID,
    template_version_id: UUID,
) -> WorkflowTemplateVersion | None:
    statement = (
        select(WorkflowTemplateVersion)
        .join(
            WorkflowTemplate,
            WorkflowTemplate.id
            == WorkflowTemplateVersion.workflow_template_id,
        )
        .where(
            WorkflowTemplate.organization_id
            == organization_id,
            WorkflowTemplateVersion.id
            == template_version_id,
        )
    )

    return session.scalar(statement)


def get_initial_stage_definition(
    session: Session,
    template_version_id: UUID,
) -> StageDefinition | None:
    statement = (
        select(StageDefinition)
        .where(
            StageDefinition.template_version_id
            == template_version_id,
            StageDefinition.active.is_(True),
        )
        .order_by(
            StageDefinition.sequence,
            StageDefinition.code,
        )
        .limit(1)
    )

    return session.scalar(statement)


def create_work_item(
    session: Session,
    organization_id: UUID,
    work_item_data: WorkItemCreate,
    initial_stage_definition_id: UUID,
) -> WorkItem:
    work_item = WorkItem(
        organization_id=organization_id,
        template_version_id=(
            work_item_data.template_version_id
        ),
        display_name=work_item_data.display_name,
        current_stage_definition_id=(
            initial_stage_definition_id
        ),
        accountable_owner_id=(
            work_item_data.accountable_owner_id
        ),
        target_at=work_item_data.target_at,
        original_target_at=work_item_data.target_at,
    )

    session.add(work_item)
    session.flush()

    stage_history = StageHistory(
        work_item_id=work_item.id,
        stage_definition_id=initial_stage_definition_id,
        entered_by_user_id=None,
        actor_source="flowlens",
        correlation_id=uuid4(),
    )

    session.add(stage_history)
    session.commit()
    session.refresh(work_item)

    return work_item


def list_work_items(
    session: Session,
    organization_id: UUID,
) -> list[WorkItem]:
    statement = (
        select(WorkItem)
        .where(
            WorkItem.organization_id == organization_id,
        )
        .order_by(
            WorkItem.created_at.desc(),
            WorkItem.id,
        )
    )

    return list(session.scalars(statement).all())


def get_work_item(
    session: Session,
    organization_id: UUID,
    work_item_id: UUID,
) -> WorkItem | None:
    statement = select(WorkItem).where(
        WorkItem.organization_id == organization_id,
        WorkItem.id == work_item_id,
    )

    return session.scalar(statement)


def get_field_definition_for_work_item(
    session: Session,
    work_item: WorkItem,
    field_definition_id: UUID,
) -> FieldDefinition | None:
    statement = select(FieldDefinition).where(
        FieldDefinition.template_version_id
        == work_item.template_version_id,
        FieldDefinition.id == field_definition_id,
    )

    return session.scalar(statement)


def get_work_item_field_value(
    session: Session,
    work_item_id: UUID,
    field_definition_id: UUID,
) -> WorkItemFieldValue | None:
    statement = select(WorkItemFieldValue).where(
        WorkItemFieldValue.work_item_id == work_item_id,
        WorkItemFieldValue.field_definition_id
        == field_definition_id,
    )

    return session.scalar(statement)


def set_work_item_field_value(
    session: Session,
    work_item: WorkItem,
    field_value_data: WorkItemFieldValueSet,
) -> WorkItemFieldValue:
    field_value = get_work_item_field_value(
        session,
        work_item.id,
        field_value_data.field_definition_id,
    )
    now = datetime.now(UTC)

    if field_value is None:
        field_value = WorkItemFieldValue(
            work_item_id=work_item.id,
            field_definition_id=(
                field_value_data.field_definition_id
            ),
            value=field_value_data.value,
            provenance_type=(
                field_value_data.provenance_type
            ),
            source_system=field_value_data.source_system,
            source_reference=(
                field_value_data.source_reference
            ),
            set_by_user_id=(
                field_value_data.set_by_user_id
            ),
            set_at=now,
        )
        session.add(field_value)
    else:
        field_value.value = field_value_data.value
        field_value.provenance_type = (
            field_value_data.provenance_type
        )
        field_value.source_system = (
            field_value_data.source_system
        )
        field_value.source_reference = (
            field_value_data.source_reference
        )
        field_value.set_by_user_id = (
            field_value_data.set_by_user_id
        )
        field_value.set_at = now

    session.commit()
    session.refresh(field_value)

    return field_value


def list_work_item_field_values(
    session: Session,
    work_item: WorkItem,
) -> list[WorkItemFieldValue]:
    statement = (
        select(WorkItemFieldValue)
        .join(
            FieldDefinition,
            FieldDefinition.id
            == WorkItemFieldValue.field_definition_id,
        )
        .where(
            WorkItemFieldValue.work_item_id
            == work_item.id,
        )
        .order_by(
            FieldDefinition.display_order,
            FieldDefinition.key,
        )
    )

    return list(session.scalars(statement).all())


def list_stage_history(
    session: Session,
    work_item_id: UUID,
) -> list[StageHistory]:
    statement = (
        select(StageHistory)
        .where(
            StageHistory.work_item_id == work_item_id,
        )
        .order_by(
            StageHistory.entered_at,
            StageHistory.id,
        )
    )

    return list(session.scalars(statement).all())


def field_value_matches_type(
    field_type: str,
    value: object,
) -> bool:
    if value is None:
        return False

    if field_type in {"text", "long_text", "url"}:
        return isinstance(value, str)

    if field_type == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )

    if field_type == "boolean":
        return isinstance(value, bool)

    if field_type == "single_choice":
        return isinstance(value, str)

    if field_type == "multi_choice":
        return (
            isinstance(value, list)
            and all(
                isinstance(item, str)
                for item in value
            )
        )

    if field_type == "date":
        if not isinstance(value, str):
            return False

        try:
            date.fromisoformat(value)
        except ValueError:
            return False

        return True

    if field_type == "datetime":
        if not isinstance(value, str):
            return False

        try:
            datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return False

        return True

    return False