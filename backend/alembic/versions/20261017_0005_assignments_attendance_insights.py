"""Sprint 5 attendance insights and assignments.

Revision ID: 20261017_0005
Revises: 20261013_0004
Create Date: 2026-10-17
"""
from alembic import op
import sqlalchemy as sa

revision = "20261017_0005"
down_revision = "20261013_0004"
branch_labels = None
depends_on = None


def _tables(bind):
    return set(sa.inspect(bind).get_table_names())


def upgrade():
    bind = op.get_bind()
    tables = _tables(bind)
    if "assignments" not in tables:
        op.create_table(
            "assignments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("due_at", sa.DateTime(), nullable=False),
            sa.Column("max_score", sa.Numeric(8, 2), nullable=False, server_default="10"),
            sa.Column("allow_late", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
            sa.Column("attachment_files", sa.Text(), nullable=True),
            sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        for col in ["due_at", "status", "created_by_user_id"]:
            op.create_index(f"ix_assignments_{col}", "assignments", [col])
    if "assignment_classes" not in tables:
        op.create_table(
            "assignment_classes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("assignment_id", sa.Integer(), sa.ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False),
            sa.Column("class_id", sa.Integer(), sa.ForeignKey("training_classes.id", ondelete="CASCADE"), nullable=False),
            sa.UniqueConstraint("assignment_id", "class_id", name="uq_assignment_class"),
        )
        op.create_index("ix_assignment_classes_assignment_id", "assignment_classes", ["assignment_id"])
        op.create_index("ix_assignment_classes_class_id", "assignment_classes", ["class_id"])
    if "assignment_extensions" not in tables:
        op.create_table(
            "assignment_extensions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("assignment_id", sa.Integer(), sa.ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False),
            sa.Column("student_id", sa.Integer(), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
            sa.Column("extended_due_at", sa.DateTime(), nullable=False),
            sa.Column("reason", sa.String(500), nullable=False),
            sa.Column("granted_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("assignment_id", "student_id", name="uq_assignment_extension_student"),
        )
        op.create_index("ix_assignment_extensions_assignment_id", "assignment_extensions", ["assignment_id"])
        op.create_index("ix_assignment_extensions_student_id", "assignment_extensions", ["student_id"])
    if "assignment_submissions" not in tables:
        op.create_table(
            "assignment_submissions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("assignment_id", sa.Integer(), sa.ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False),
            sa.Column("student_id", sa.Integer(), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
            sa.Column("version", sa.Integer(), nullable=False),
            sa.Column("file_items", sa.Text(), nullable=False),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("status", sa.String(30), nullable=False, server_default="submitted"),
            sa.Column("is_late", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("score", sa.Numeric(8, 2), nullable=True),
            sa.Column("feedback", sa.Text(), nullable=True),
            sa.Column("graded_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("graded_at", sa.DateTime(), nullable=True),
            sa.Column("submitted_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("assignment_id", "student_id", "version", name="uq_assignment_submission_version"),
        )
        for col in ["assignment_id", "student_id", "status", "is_late", "submitted_at"]:
            op.create_index(f"ix_assignment_submissions_{col}", "assignment_submissions", [col])


def downgrade():
    bind = op.get_bind()
    tables = _tables(bind)
    for table in ["assignment_submissions", "assignment_extensions", "assignment_classes", "assignments"]:
        if table in tables:
            op.drop_table(table)
