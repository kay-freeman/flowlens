from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from flowlens.database import get_database_session
from flowlens.models import WorkflowTemplateVersion
from flowlens.schemas import (
    FieldDefinitionCreate,
    FieldDefinitionResponse,
    StageDefinitionCreate,
    StageDefinitionResponse,
)
from flowlens.services.organizations import get_organization
from flowlens.services.roles import get_role
from flowlens.services.workflow_definitions import (
    create_field_definition,
    create_stage_definition,
    get_field_definition,
    get_field_definition_by_key,
    get_stage_definition,
    get_stage_definition_by_code,
    list_field_definitions,
    list_stage_definitions,
)
from flowlens.services.workflow_templates import (
    get_workflow_template,
    get_workflow_template_version,
)


router = APIRouter(
    prefix=(
        "/organizations/{organization_id}"
        "/workflow-templates/{workflow_template_id}"
        "/versions/{workflow_template_version_id}"
    ),
    tags=["Workflow Definitions"],
)


def require_workflow_template_version(
    session: Session,
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
) -> WorkflowTemplateVersion:
    organization = get_organization(
        session,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
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

    workflow_template_version = get_workflow_template_version(
        session,
        workflow_template_id,
        workflow_template_version_id,
    )

    if workflow_template_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template version not found.",
        )

    return workflow_template_version


def require_draft_version(
    workflow_template_version: WorkflowTemplateVersion,
) -> None:
    if workflow_template_version.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Definitions can only be changed on draft "
                "workflow template versions."
            ),
        )


@router.post(
    "/stages",
    response_model=StageDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a stage definition",
)
def create_stage_definition_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
    stage_data: StageDefinitionCreate,
    session: Session = Depends(get_database_session),
) -> StageDefinitionResponse:
    workflow_template_version = (
        require_workflow_template_version(
            session,
            organization_id,
            workflow_template_id,
            workflow_template_version_id,
        )
    )
    require_draft_version(workflow_template_version)

    if stage_data.default_owner_role_id is not None:
        default_owner_role = get_role(
            session,
            organization_id,
            stage_data.default_owner_role_id,
        )

        if default_owner_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Default owner role not found.",
            )

    existing_stage = get_stage_definition_by_code(
        session,
        workflow_template_version_id,
        stage_data.code,
    )

    if existing_stage is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A stage definition with this code already "
                "exists in the workflow template version."
            ),
        )

    try:
        stage_definition = create_stage_definition(
            session,
            workflow_template_version_id,
            stage_data,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A stage definition with this code already "
                "exists in the workflow template version."
            ),
        ) from exc

    return StageDefinitionResponse.model_validate(
        stage_definition
    )


@router.get(
    "/stages",
    response_model=list[StageDefinitionResponse],
    summary="List stage definitions",
)
def list_stage_definitions_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
    session: Session = Depends(get_database_session),
) -> list[StageDefinitionResponse]:
    require_workflow_template_version(
        session,
        organization_id,
        workflow_template_id,
        workflow_template_version_id,
    )

    stage_definitions = list_stage_definitions(
        session,
        workflow_template_version_id,
    )

    return [
        StageDefinitionResponse.model_validate(
            stage_definition
        )
        for stage_definition in stage_definitions
    ]


@router.get(
    "/stages/{stage_definition_id}",
    response_model=StageDefinitionResponse,
    summary="Retrieve a stage definition",
)
def get_stage_definition_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
    stage_definition_id: UUID,
    session: Session = Depends(get_database_session),
) -> StageDefinitionResponse:
    require_workflow_template_version(
        session,
        organization_id,
        workflow_template_id,
        workflow_template_version_id,
    )

    stage_definition = get_stage_definition(
        session,
        workflow_template_version_id,
        stage_definition_id,
    )

    if stage_definition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage definition not found.",
        )

    return StageDefinitionResponse.model_validate(
        stage_definition
    )


@router.post(
    "/fields",
    response_model=FieldDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a field definition",
)
def create_field_definition_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
    field_data: FieldDefinitionCreate,
    session: Session = Depends(get_database_session),
) -> FieldDefinitionResponse:
    workflow_template_version = (
        require_workflow_template_version(
            session,
            organization_id,
            workflow_template_id,
            workflow_template_version_id,
        )
    )
    require_draft_version(workflow_template_version)

    existing_field = get_field_definition_by_key(
        session,
        workflow_template_version_id,
        field_data.key,
    )

    if existing_field is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A field definition with this key already "
                "exists in the workflow template version."
            ),
        )

    try:
        field_definition = create_field_definition(
            session,
            workflow_template_version_id,
            field_data,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A field definition with this key already "
                "exists in the workflow template version."
            ),
        ) from exc

    return FieldDefinitionResponse.model_validate(
        field_definition
    )


@router.get(
    "/fields",
    response_model=list[FieldDefinitionResponse],
    summary="List field definitions",
)
def list_field_definitions_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
    session: Session = Depends(get_database_session),
) -> list[FieldDefinitionResponse]:
    require_workflow_template_version(
        session,
        organization_id,
        workflow_template_id,
        workflow_template_version_id,
    )

    field_definitions = list_field_definitions(
        session,
        workflow_template_version_id,
    )

    return [
        FieldDefinitionResponse.model_validate(
            field_definition
        )
        for field_definition in field_definitions
    ]


@router.get(
    "/fields/{field_definition_id}",
    response_model=FieldDefinitionResponse,
    summary="Retrieve a field definition",
)
def get_field_definition_endpoint(
    organization_id: UUID,
    workflow_template_id: UUID,
    workflow_template_version_id: UUID,
    field_definition_id: UUID,
    session: Session = Depends(get_database_session),
) -> FieldDefinitionResponse:
    require_workflow_template_version(
        session,
        organization_id,
        workflow_template_id,
        workflow_template_version_id,
    )

    field_definition = get_field_definition(
        session,
        workflow_template_version_id,
        field_definition_id,
    )

    if field_definition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field definition not found.",
        )

    return FieldDefinitionResponse.model_validate(
        field_definition
    )