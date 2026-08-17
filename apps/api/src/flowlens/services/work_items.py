from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from flowlens.models import (
    StageDefinition,
    WorkItem,
    WorkflowTemplate,
    WorkflowTemplateVersion,
)
from flowlens.schemas import WorkItemCreate


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