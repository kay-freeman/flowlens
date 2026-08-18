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
from flowlens.models import WorkItem
from flowlens.schemas import (
    StageHistoryResponse,
    WorkItemCreate,
    WorkItemFieldValueResponse,
    WorkItemFieldValueSet,
    WorkItemResponse,
)
from flowlens.services.organizations import get_organization
from flowlens.services.users import get_user
from flowlens.services.work_items import (
    create_work_item,
    field_value_matches_type,
    get_field_definition_for_work_item,
    get_initial_stage_definition,
    get_work_item,
    get_workflow_template_version_for_organization,
    list_stage_history,
    list_work_item_field_values,
    list_work_items,
    set_work_item_field_value,
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


def require_work_item(
    session: Session,
    organization_id: UUID,
    work_item_id: UUID,
) -> WorkItem:
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

    return work_item


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
    work_item = require_work_item(
        session,
        organization_id,
        work_item_id,
    )

    return WorkItemResponse.model_validate(work_item)


@router.put(
    "/{work_item_id}/field-values",
    response_model=WorkItemFieldValueResponse,
    summary="Set a work-item field value",
)
def set_work_item_field_value_endpoint(
    organization_id: UUID,
    work_item_id: UUID,
    field_value_data: WorkItemFieldValueSet,
    session: Session = Depends(get_database_session),
) -> WorkItemFieldValueResponse:
    work_item = require_work_item(
        session,
        organization_id,
        work_item_id,
    )

    if work_item.status in {"completed", "canceled"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Field values cannot be changed on a "
                "completed or canceled work item."
            ),
        )

    field_definition = (
        get_field_definition_for_work_item(
            session,
            work_item,
            field_value_data.field_definition_id,
        )
    )

    if field_definition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field definition not found.",
        )

    if (
        field_value_data.provenance_type.value
        != field_definition.source_type
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=(
                "The provenance type does not match the "
                "field definition source type."
            ),
        )

    if not field_value_matches_type(
        field_definition.field_type,
        field_value_data.value,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=(
                "The value does not match the configured "
                "field type."
            ),
        )

    if (
        field_value_data.provenance_type.value
        == "external"
        and field_value_data.source_system is None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=(
                "External field values require a "
                "source system."
            ),
        )

    if (
        field_value_data.provenance_type.value
        == "user_entered"
        and field_value_data.set_by_user_id is None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=(
                "User-entered field values require a "
                "setting user."
            ),
        )

    if field_value_data.set_by_user_id is not None:
        setting_user = get_user(
            session,
            organization_id,
            field_value_data.set_by_user_id,
        )

        if setting_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setting user not found.",
            )

        if not setting_user.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Setting user must be active.",
            )

    try:
        field_value = set_work_item_field_value(
            session,
            work_item,
            field_value_data,
        )
    except IntegrityError as exc:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The work-item field value could not "
                "be saved."
            ),
        ) from exc

    return WorkItemFieldValueResponse.model_validate(
        field_value
    )


@router.get(
    "/{work_item_id}/field-values",
    response_model=list[WorkItemFieldValueResponse],
    summary="List work-item field values",
)
def list_work_item_field_values_endpoint(
    organization_id: UUID,
    work_item_id: UUID,
    session: Session = Depends(get_database_session),
) -> list[WorkItemFieldValueResponse]:
    work_item = require_work_item(
        session,
        organization_id,
        work_item_id,
    )

    field_values = list_work_item_field_values(
        session,
        work_item,
    )

    return [
        WorkItemFieldValueResponse.model_validate(
            field_value
        )
        for field_value in field_values
    ]


@router.get(
    "/{work_item_id}/stage-history",
    response_model=list[StageHistoryResponse],
    summary="List work-item stage history",
)
def list_stage_history_endpoint(
    organization_id: UUID,
    work_item_id: UUID,
    session: Session = Depends(get_database_session),
) -> list[StageHistoryResponse]:
    work_item = require_work_item(
        session,
        organization_id,
        work_item_id,
    )

    stage_history = list_stage_history(
        session,
        work_item.id,
    )

    return [
        StageHistoryResponse.model_validate(history)
        for history in stage_history
    ]