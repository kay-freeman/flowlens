from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from flowlens.database import get_database_session
from flowlens.models import WorkflowTemplate
from flowlens.schemas import (
    WorkflowTemplateCreate,
    WorkflowTemplateResponse,
)
from flowlens.services.organizations import get_organization
from flowlens.services.workflow_templates import (
    create_workflow_template,
    get_workflow_template,
    get_workflow_template_by_slug,
    list_workflow_templates,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/workflow-templates",
    tags=["Workflow Templates"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_database_session),
]


def require_organization(
    session: Session,
    organization_id: UUID,
) -> None:
    organization = get_organization(
        session,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )


@router.post(
    "",
    response_model=WorkflowTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workflow template",
)
def create_workflow_template_endpoint(
    organization_id: UUID,
    template_data: WorkflowTemplateCreate,
    session: DatabaseSession,
) -> WorkflowTemplate:
    require_organization(
        session,
        organization_id,
    )

    existing_template = get_workflow_template_by_slug(
        session,
        organization_id,
        template_data.slug,
    )

    if existing_template is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A workflow template with this slug "
                "already exists in the organization."
            ),
        )

    try:
        return create_workflow_template(
            session,
            organization_id,
            template_data,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A workflow template with this slug "
                "already exists in the organization."
            ),
        ) from exc


@router.get(
    "",
    response_model=list[WorkflowTemplateResponse],
    summary="List workflow templates",
)
def list_workflow_templates_endpoint(
    organization_id: UUID,
    session: DatabaseSession,
) -> list[WorkflowTemplate]:
    require_organization(
        session,
        organization_id,
    )

    return list_workflow_templates(
        session,
        organization_id,
    )


@router.get(
    "/{workflow_template_id}",
    response_model=WorkflowTemplateResponse,
    summary="Retrieve a workflow template",
)
def get_workflow_template_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    session: DatabaseSession,
) -> WorkflowTemplate:
    require_organization(
        session,
        organization_id,
    )

    workflow_template = get_workflow_template(
        session,
        organization_id,
        workflow_template_id,
    )

    if workflow_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found.",
        )

    return workflow_template