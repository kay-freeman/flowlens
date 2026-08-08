from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from flowlens.database import get_database_session
from flowlens.schemas import (
    WorkflowTemplateCreate,
    WorkflowTemplateResponse,
    WorkflowTemplateVersionCreate,
    WorkflowTemplateVersionResponse,
)
from flowlens.services.organizations import get_organization
from flowlens.services.users import get_user
from flowlens.services.workflow_templates import (
    create_workflow_template,
    create_workflow_template_version,
    get_workflow_template,
    get_workflow_template_by_slug,
    get_workflow_template_version,
    list_workflow_template_versions,
    list_workflow_templates,
    publish_workflow_template_version,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/workflow-templates",
    tags=["Workflow Templates"],
)


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


def require_workflow_template(
    session: Session,
    organization_id: UUID,
    workflow_template_id: UUID,
):
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


@router.post(
    "",
    response_model=WorkflowTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workflow template",
)
def create_workflow_template_endpoint(
    organization_id: UUID,
    template_data: WorkflowTemplateCreate,
    session: Session = Depends(get_database_session),
) -> WorkflowTemplateResponse:
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
        workflow_template = create_workflow_template(
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

    return WorkflowTemplateResponse.model_validate(
        workflow_template
    )


@router.get(
    "",
    response_model=list[WorkflowTemplateResponse],
    summary="List workflow templates",
)
def list_workflow_templates_endpoint(
    organization_id: UUID,
    session: Session = Depends(get_database_session),
) -> list[WorkflowTemplateResponse]:
    require_organization(
        session,
        organization_id,
    )

    workflow_templates = list_workflow_templates(
        session,
        organization_id,
    )

    return [
        WorkflowTemplateResponse.model_validate(
            workflow_template
        )
        for workflow_template in workflow_templates
    ]


@router.get(
    "/{workflow_template_id}",
    response_model=WorkflowTemplateResponse,
    summary="Retrieve a workflow template",
)
def get_workflow_template_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    session: Session = Depends(get_database_session),
) -> WorkflowTemplateResponse:
    workflow_template = require_workflow_template(
        session,
        organization_id,
        workflow_template_id,
    )

    return WorkflowTemplateResponse.model_validate(
        workflow_template
    )


@router.post(
    "/{workflow_template_id}/versions",
    response_model=WorkflowTemplateVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workflow template version",
)
def create_workflow_template_version_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    version_data: WorkflowTemplateVersionCreate,
    session: Session = Depends(get_database_session),
) -> WorkflowTemplateVersionResponse:
    require_workflow_template(
        session,
        organization_id,
        workflow_template_id,
    )

    try:
        workflow_template_version = (
            create_workflow_template_version(
                session,
                workflow_template_id,
                version_data,
            )
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The next workflow template version "
                "could not be created."
            ),
        ) from exc

    return WorkflowTemplateVersionResponse.model_validate(
        workflow_template_version
    )


@router.get(
    "/{workflow_template_id}/versions",
    response_model=list[WorkflowTemplateVersionResponse],
    summary="List workflow template versions",
)
def list_workflow_template_versions_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    session: Session = Depends(get_database_session),
) -> list[WorkflowTemplateVersionResponse]:
    require_workflow_template(
        session,
        organization_id,
        workflow_template_id,
    )

    workflow_template_versions = (
        list_workflow_template_versions(
            session,
            workflow_template_id,
        )
    )

    return [
        WorkflowTemplateVersionResponse.model_validate(
            workflow_template_version
        )
        for workflow_template_version
        in workflow_template_versions
    ]


@router.get(
    "/{workflow_template_id}/versions/"
    "{workflow_template_version_id}",
    response_model=WorkflowTemplateVersionResponse,
    summary="Retrieve a workflow template version",
)
def get_workflow_template_version_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
    session: Session = Depends(get_database_session),
) -> WorkflowTemplateVersionResponse:
    require_workflow_template(
        session,
        organization_id,
        workflow_template_id,
    )

    workflow_template_version = (
        get_workflow_template_version(
            session,
            workflow_template_id,
            workflow_template_version_id,
        )
    )

    if workflow_template_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template version not found.",
        )

    return WorkflowTemplateVersionResponse.model_validate(
        workflow_template_version
    )


@router.post(
    "/{workflow_template_id}/versions/"
    "{workflow_template_version_id}/publish",
    response_model=WorkflowTemplateVersionResponse,
    summary="Publish a workflow template version",
)
def publish_workflow_template_version_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
    published_by_user_id: Annotated[
        UUID,
        Body(embed=True),
    ],
    session: Session = Depends(get_database_session),
) -> WorkflowTemplateVersionResponse:
    workflow_template = require_workflow_template(
        session,
        organization_id,
        workflow_template_id,
    )

    workflow_template_version = (
        get_workflow_template_version(
            session,
            workflow_template_id,
            workflow_template_version_id,
        )
    )

    if workflow_template_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template version not found.",
        )

    if workflow_template_version.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only draft workflow template versions "
                "can be published."
            ),
        )

    publishing_user = get_user(
        session,
        organization_id,
        published_by_user_id,
    )

    if publishing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publishing user not found.",
        )

    published_version = publish_workflow_template_version(
        session,
        workflow_template,
        workflow_template_version,
        published_by_user_id,
    )

    return WorkflowTemplateVersionResponse.model_validate(
        published_version
    )