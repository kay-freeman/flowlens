from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from flowlens.models import (
    WorkflowTemplate,
    WorkflowTemplateVersion,
)
from flowlens.schemas import (
    WorkflowTemplateCreate,
    WorkflowTemplateVersionCreate,
)


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
            == organization_id,
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


def create_workflow_template_version(
    session: Session,
    workflow_template_id: UUID,
    version_data: WorkflowTemplateVersionCreate,
) -> WorkflowTemplateVersion:
    version_number_statement = select(
        func.coalesce(
            func.max(
                WorkflowTemplateVersion.version_number
            ),
            0,
        )
        + 1
    ).where(
        WorkflowTemplateVersion.workflow_template_id
        == workflow_template_id,
    )

    version_number = session.scalar(
        version_number_statement
    )

    workflow_template_version = WorkflowTemplateVersion(
        workflow_template_id=workflow_template_id,
        version_number=version_number,
        change_summary=version_data.change_summary,
    )

    session.add(workflow_template_version)
    session.commit()
    session.refresh(workflow_template_version)

    return workflow_template_version


def list_workflow_template_versions(
    session: Session,
    workflow_template_id: UUID,
) -> list[WorkflowTemplateVersion]:
    statement = (
        select(WorkflowTemplateVersion)
        .where(
            WorkflowTemplateVersion.workflow_template_id
            == workflow_template_id,
        )
        .order_by(
            WorkflowTemplateVersion.version_number,
        )
    )

    return list(session.scalars(statement).all())


def get_workflow_template_version(
    session: Session,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
) -> WorkflowTemplateVersion | None:
    statement = select(
        WorkflowTemplateVersion
    ).where(
        WorkflowTemplateVersion.workflow_template_id
        == workflow_template_id,
        WorkflowTemplateVersion.id
        == workflow_template_version_id,
    )

    return session.scalar(statement)


def publish_workflow_template_version(
    session: Session,
    workflow_template: WorkflowTemplate,
    workflow_template_version: WorkflowTemplateVersion,
    published_by_user_id: UUID,
) -> WorkflowTemplateVersion:
    published_versions_statement = select(
        WorkflowTemplateVersion
    ).where(
        WorkflowTemplateVersion.workflow_template_id
        == workflow_template.id,
        WorkflowTemplateVersion.status == "published",
    )

    published_versions = session.scalars(
        published_versions_statement
    ).all()

    for published_version in published_versions:
        published_version.status = "retired"

    workflow_template_version.status = "published"
    workflow_template_version.published_at = datetime.now(UTC)
    workflow_template_version.published_by_user_id = (
        published_by_user_id
    )

    workflow_template.status = "active"

    session.commit()
    session.refresh(workflow_template_version)

    return workflow_template_version