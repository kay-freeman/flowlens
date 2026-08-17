from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from flowlens.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "email",
            name="uq_users_organization_email",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    department: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    identity_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    external_subject: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "code",
            name="uq_roles_organization_code",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    permissions: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default="[]",
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            name="uq_user_roles_user_role",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    role_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    assigned_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )


class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_workflow_templates_organization_slug",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    work_item_label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    work_item_label_plural: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        server_default="draft",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class WorkflowTemplateVersion(Base):
    __tablename__ = "workflow_template_versions"
    __table_args__ = (
        UniqueConstraint(
            "workflow_template_id",
            "version_number",
            name="uq_workflow_template_versions_template_number",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    workflow_template_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "workflow_templates.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        server_default="draft",
    )
    change_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    published_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class StageDefinition(Base):
    __tablename__ = "stage_definitions"
    __table_args__ = (
        UniqueConstraint(
            "template_version_id",
            "code",
            name="uq_stage_definitions_version_code",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "workflow_template_versions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    default_owner_role_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "roles.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    sla_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    terminal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )


class FieldDefinition(Base):
    __tablename__ = "field_definitions"
    __table_args__ = (
        UniqueConstraint(
            "template_version_id",
            "key",
            name="uq_field_definitions_version_key",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "workflow_template_versions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    field_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    source_system: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    validation_config: Mapped[dict[str, object] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    sensitive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )


class WorkItem(Base):
    __tablename__ = "work_items"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "workflow_template_versions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        server_default="active",
    )
    current_stage_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "stage_definitions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    risk_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="on_track",
        server_default="on_track",
    )
    accountable_owner_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    target_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    original_target_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    pause_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )