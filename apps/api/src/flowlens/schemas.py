from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class IdentitySource(StrEnum):
    DEMO = "demo"
    LOCAL = "local"
    EXTERNAL = "external"


class TemplateStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class VersionStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    RETIRED = "retired"


class FieldType(StrEnum):
    TEXT = "text"
    LONG_TEXT = "long_text"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    URL = "url"


class ProvenanceType(StrEnum):
    EXTERNAL = "external"
    USER_ENTERED = "user_entered"
    CALCULATED = "calculated"
    DERIVED = "derived"
    IMPORTED = "imported"


class ActorSource(StrEnum):
    USER = "user"
    FLOWLENS = "flowlens"
    EXTERNAL_SYSTEM = "external_system"
    IMPORT = "import"


class WorkItemStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELED = "canceled"


class RiskStatus(StrEnum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
    PAUSED = "paused"


class OrganizationCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
        examples=["Northstar Business Services"],
    )
    slug: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        examples=["northstar-business-services"],
    )


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: str = Field(
        min_length=3,
        max_length=320,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        examples=["maya.chen@northstar.example"],
    )
    display_name: str = Field(
        min_length=1,
        max_length=200,
        examples=["Maya Chen"],
    )
    department: str | None = Field(
        default=None,
        max_length=200,
        examples=["Operations"],
    )
    identity_source: IdentitySource = IdentitySource.DEMO
    external_subject: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("display_name", mode="before")
    @classmethod
    def normalize_display_name(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("department", mode="before")
    @classmethod
    def normalize_department(cls, value: object) -> object:
        if isinstance(value, str):
            normalized_value = value.strip()

            return normalized_value or None

        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    email: str
    display_name: str
    department: str | None
    identity_source: IdentitySource
    external_subject: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class RoleCreate(BaseModel):
    code: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z][a-z0-9_]*$",
        examples=["operations_manager"],
    )
    name: str = Field(
        min_length=1,
        max_length=200,
        examples=["Operations Manager"],
    )
    description: str = Field(
        min_length=1,
        max_length=1000,
        examples=[
            "Manages operational workflow assignments and exceptions."
        ],
    )
    permissions: list[str] = Field(
        default_factory=list,
        examples=[
            [
                "work_items:read",
                "work_items:update",
                "exceptions:manage",
            ]
        ],
    )

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("name", "description", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("permissions")
    @classmethod
    def normalize_permissions(
        cls,
        permissions: list[str],
    ) -> list[str]:
        normalized_permissions = {
            permission.strip().lower()
            for permission in permissions
            if permission.strip()
        }

        return sorted(normalized_permissions)


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    code: str
    name: str
    description: str
    permissions: list[str]
    active: bool


class UserRoleCreate(BaseModel):
    role_id: UUID
    assigned_by_user_id: UUID | None = None


class UserRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    role_id: UUID
    assigned_at: datetime
    assigned_by_user_id: UUID | None


class WorkflowTemplateCreate(BaseModel):
    slug: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        examples=["contract-to-launch"],
    )
    name: str = Field(
        min_length=1,
        max_length=200,
        examples=["Contract-to-Launch"],
    )
    work_item_label: str = Field(
        min_length=1,
        max_length=100,
        examples=["Launch"],
    )
    work_item_label_plural: str = Field(
        min_length=1,
        max_length=100,
        examples=["Launches"],
    )
    description: str = Field(
        min_length=1,
        max_length=2000,
        examples=[
            "Coordinates work from signed contract through customer launch."
        ],
    )

    @field_validator("slug", mode="before")
    @classmethod
    def normalize_slug(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator(
        "name",
        "work_item_label",
        "work_item_label_plural",
        "description",
        mode="before",
    )
    @classmethod
    def normalize_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value


class WorkflowTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    slug: str
    name: str
    work_item_label: str
    work_item_label_plural: str
    description: str
    status: TemplateStatus
    created_at: datetime
    updated_at: datetime


class WorkflowTemplateVersionCreate(BaseModel):
    change_summary: str = Field(
        min_length=1,
        max_length=2000,
        examples=[
            "Initial contract-to-launch workflow configuration."
        ],
    )

    @field_validator("change_summary", mode="before")
    @classmethod
    def normalize_change_summary(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value


class WorkflowTemplateVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_template_id: UUID
    version_number: int = Field(ge=1)
    status: VersionStatus
    change_summary: str
    published_at: datetime | None
    published_by_user_id: UUID | None
    created_at: datetime


class StageDefinitionCreate(BaseModel):
    code: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z][a-z0-9_]*$",
        examples=["validation"],
    )
    name: str = Field(
        min_length=1,
        max_length=200,
        examples=["Validation"],
    )
    sequence: int = Field(
        ge=1,
        examples=[2],
    )
    description: str = Field(
        min_length=1,
        max_length=2000,
        examples=[
            "Validate contract, customer, and billing information."
        ],
    )
    default_owner_role_id: UUID | None = None
    sla_minutes: int | None = Field(
        default=None,
        ge=1,
        examples=[1440],
    )
    terminal: bool = False
    active: bool = True

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("name", "description", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value


class StageDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_version_id: UUID
    code: str
    name: str
    sequence: int = Field(ge=1)
    description: str
    default_owner_role_id: UUID | None
    sla_minutes: int | None
    terminal: bool
    active: bool


class FieldDefinitionCreate(BaseModel):
    key: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z][a-z0-9_]*$",
        examples=["contract_value"],
    )
    label: str = Field(
        min_length=1,
        max_length=200,
        examples=["Contract Value"],
    )
    field_type: FieldType
    required: bool = False
    source_type: ProvenanceType
    source_system: str | None = Field(
        default=None,
        max_length=200,
        examples=["Salesforce"],
    )
    validation_config: dict[str, object] | None = None
    display_order: int = Field(
        ge=1,
        examples=[3],
    )
    sensitive: bool = False

    @field_validator("key", mode="before")
    @classmethod
    def normalize_key(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("label", mode="before")
    @classmethod
    def normalize_label(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("source_system", mode="before")
    @classmethod
    def normalize_source_system(cls, value: object) -> object:
        if isinstance(value, str):
            normalized_value = value.strip()

            return normalized_value or None

        return value


class FieldDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_version_id: UUID
    key: str
    label: str
    field_type: FieldType
    required: bool
    source_type: ProvenanceType
    source_system: str | None
    validation_config: dict[str, object] | None
    display_order: int = Field(ge=1)
    sensitive: bool


class WorkItemCreate(BaseModel):
    template_version_id: UUID
    display_name: str = Field(
        min_length=1,
        max_length=200,
        examples=["Northstar Customer Launch"],
    )
    accountable_owner_id: UUID
    target_at: datetime | None = Field(
        default=None,
        examples=["2026-09-30T17:00:00Z"],
    )

    @field_validator("display_name", mode="before")
    @classmethod
    def normalize_display_name(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()

        return value


class WorkItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    template_version_id: UUID
    display_name: str
    status: WorkItemStatus
    current_stage_definition_id: UUID
    risk_status: RiskStatus
    accountable_owner_id: UUID
    target_at: datetime | None
    original_target_at: datetime | None
    paused_at: datetime | None
    pause_reason: str | None
    completed_at: datetime | None
    canceled_at: datetime | None
    cancellation_reason: str | None
    created_at: datetime
    updated_at: datetime
    version: int = Field(ge=1)


class WorkItemFieldValueSet(BaseModel):
    field_definition_id: UUID
    value: object
    provenance_type: ProvenanceType
    source_system: str | None = Field(
        default=None,
        max_length=200,
        examples=["Salesforce"],
    )
    source_reference: str | None = Field(
        default=None,
        max_length=500,
        examples=["opportunity-1842"],
    )
    set_by_user_id: UUID | None = None

    @field_validator(
        "source_system",
        "source_reference",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: object,
    ) -> object:
        if isinstance(value, str):
            normalized_value = value.strip()

            return normalized_value or None

        return value


class WorkItemFieldValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    work_item_id: UUID
    field_definition_id: UUID
    value: object
    provenance_type: ProvenanceType
    source_system: str | None
    source_reference: str | None
    set_by_user_id: UUID | None
    set_at: datetime
    updated_at: datetime


class StageHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    work_item_id: UUID
    stage_definition_id: UUID
    entered_at: datetime
    exited_at: datetime | None
    entered_by_user_id: UUID | None
    actor_source: ActorSource
    exit_reason: str | None
    correlation_id: UUID