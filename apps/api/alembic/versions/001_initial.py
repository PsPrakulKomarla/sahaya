"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("preferred_language", sa.String(), nullable=False, server_default="en"),
        sa.Column("profile", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "services",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("jurisdiction", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=False),
        sa.Column("official_portal", sa.String(), nullable=False),
        sa.Column("capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("required_documents", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("adapter", sa.String(), nullable=False),
        sa.Column("workflow_version", sa.String(), nullable=False),
        sa.Column("last_verified", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("extracted_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("verification_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_user_id"), "documents", ["user_id"], unique=False)

    op.create_table(
        "applications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("service_id", sa.String(), nullable=False),
        sa.Column("reference_number", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("form_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("documents", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timeline", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("next_action", sa.String(), nullable=True),
        sa.Column("grievance_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_applications_user_id"), "applications", ["user_id"], unique=False)
    op.create_index(op.f("ix_applications_service_id"), "applications", ["service_id"], unique=False)

    op.create_table(
        "grievances",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("application_id", sa.String(), nullable=True),
        sa.Column("service_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("reference_number", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_grievances_user_id"), "grievances", ["user_id"], unique=False)

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("intent", sa.String(), nullable=False),
        sa.Column("service_id", sa.String(), nullable=True),
        sa.Column("portal", sa.String(), nullable=True),
        sa.Column("current_state", sa.String(), nullable=False),
        sa.Column("actions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("errors", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recovery_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("human_approvals", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("final_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_runs_user_id"), "agent_runs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_runs_user_id"), table_name="agent_runs")
    op.drop_table("agent_runs")
    op.drop_index(op.f("ix_grievances_user_id"), table_name="grievances")
    op.drop_table("grievances")
    op.drop_index(op.f("ix_applications_service_id"), table_name="applications")
    op.drop_index(op.f("ix_applications_user_id"), table_name="applications")
    op.drop_table("applications")
    op.drop_index(op.f("ix_documents_user_id"), table_name="documents")
    op.drop_table("documents")
    op.drop_table("services")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")