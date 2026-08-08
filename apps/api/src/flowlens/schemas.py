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