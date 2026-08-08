from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from flowlens.models import WorkflowTemplate
from flowlens.schemas import WorkflowTemplateCreate


def create_workflow_template(
    session: Session,
    organization_id: UUID,
    template_data: WorkflowTemplateCreate,
) -> WorkflowTemplate:
    workflow_template = WorkflowTemplate(
        organization_id=organization_id,
        slug=template_data.slug,
        name=template_data.name,
        work_item_label=template_data.work_item_label,
        work_item_label_plural=(
            template_data.work_item_label_plural
        ),
        description=template_data.description,
    )

    session.add(workflow_template)
    session.commit()
    session.refresh(workflow_template)

    return workflow_template


def list_workflow_templates(
    session: Session,
    organization_id: UUID,
) -> list[WorkflowTemplate]:
    statement = (
        select(WorkflowTemplate)
        .where(
            WorkflowTemplate.organization_id
            == organization_id
        )
        .order_by(
            WorkflowTemplate.name,
            WorkflowTemplate.slug,
        )
    )

    return list(session.scalars(statement).all())


def get_workflow_template(
    session: Session,
    organization_id: UUID,
    workflow_template_id: UUID,
) -> WorkflowTemplate | None:
    statement = select(WorkflowTemplate).where(
        WorkflowTemplate.organization_id
        == organization_id,
        WorkflowTemplate.id == workflow_template_id,
    )

    return session.scalar(statement)


def get_workflow_template_by_slug(
    session: Session,
    organization_id: UUID,
    slug: str,
) -> WorkflowTemplate | None:
    statement = select(WorkflowTemplate).where(
        WorkflowTemplate.organization_id
        == organization_id,
        WorkflowTemplate.slug == slug,
    )

    return session.scalar(statement)