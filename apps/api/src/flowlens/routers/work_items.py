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
from flowlens.schemas import (
    WorkItemCreate,
    WorkItemResponse,
)
from flowlens.services.organizations import get_organization
from flowlens.services.users import get_user
from flowlens.services.work_items import (
    create_work_item,
    get_initial_stage_definition,
    get_work_item,
    get_workflow_template_version_for_organization,
    list_work_items,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/work-items",
    tags=["Work Items"],
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


@router.post(
    "",
    response_model=WorkItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a work item",
)
def create_work_item_endpoint(
    organization_id: UUID,
    work_item_data: WorkItemCreate,
    session: Session = Depends(get_database_session),
) -> WorkItemResponse:
    require_organization(
        session,
        organization_id,
    )

    template_version = (
        get_workflow_template_version_for_organization(
            session,
            organization_id,
            work_item_data.template_version_id,
        )
    )

    if template_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template version not found.",
        )

    if template_version.status != "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Work items can only be created from a "
                "published workflow template version."
            ),
        )

    accountable_owner = get_user(
        session,
        organization_id,
        work_item_data.accountable_owner_id,
    )

    if accountable_owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accountable owner not found.",
        )

    if not accountable_owner.active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Accountable owner must be active.",
        )

    initial_stage = get_initial_stage_definition(
        session,
        work_item_data.template_version_id,
    )

    if initial_stage is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The workflow template version must have "
                "an active stage before creating work items."
            ),
        )

    try:
        work_item = create_work_item(
            session,
            organization_id,
            work_item_data,
            initial_stage.id,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The work item could not be created.",
        ) from exc

    return WorkItemResponse.model_validate(work_item)


@router.get(
    "",
    response_model=list[WorkItemResponse],
    summary="List work items",
)
def list_work_items_endpoint(
    organization_id: UUID,
    session: Session = Depends(get_database_session),
) -> list[WorkItemResponse]:
    require_organization(
        session,
        organization_id,
    )

    work_items = list_work_items(
        session,
        organization_id,
    )

    return [
        WorkItemResponse.model_validate(work_item)
        for work_item in work_items
    ]


@router.get(
    "/{work_item_id}",
    response_model=WorkItemResponse,
    summary="Retrieve a work item",
)
def get_work_item_endpoint(
    organization_id: UUID,
    work_item_id: UUID,
    session: Session = Depends(get_database_session),
) -> WorkItemResponse:
    require_organization(
        session,
        organization_id,
    )

    work_item = get_work_item(
        session,
        organization_id,
        work_item_id,
    )

    if work_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work item not found.",
        )

    return WorkItemResponse.model_validate(work_item)