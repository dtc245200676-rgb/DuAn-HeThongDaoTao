"""Sprint 2 profile, training catalog and admissions leads.

Revision ID: 20261006_0002
Revises: 20261004_0001
Create Date: 2026-10-06
"""
from alembic import op
import sqlalchemy as sa

revision = "20261006_0002"
down_revision = "20261004_0001"
branch_labels = None
depends_on = None


def _tables(bind): return set(sa.inspect(bind).get_table_names())
def _cols(bind, table): return {x["name"] for x in sa.inspect(bind).get_columns(table)}


def upgrade():
    bind = op.get_bind()
    tables = _tables(bind)
    if "users" in tables:
        cols = _cols(bind, "users")
        for name, col in [
            ("date_of_birth", sa.Column("date_of_birth", sa.Date(), nullable=True)),
            ("address", sa.Column("address", sa.String(500), nullable=True)),
            ("avatar_path", sa.Column("avatar_path", sa.String(500), nullable=True)),
            ("avatar_thumbnail_path", sa.Column("avatar_thumbnail_path", sa.String(500), nullable=True)),
        ]:
            if name not in cols: op.add_column("users", col)

    tables = _tables(bind)
    if "training_programs" not in tables:
        op.create_table("training_programs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(50), nullable=False),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("total_duration_hours", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("standard_tuition", sa.Numeric(14,2), nullable=False, server_default="0"),
            sa.Column("status", sa.String(20), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("code", name="uq_training_programs_code"))
        op.create_index("ix_training_programs_code", "training_programs", ["code"], unique=True)
        op.create_index("ix_training_programs_status", "training_programs", ["status"])

    if "subjects" not in tables:
        op.create_table("subjects",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(50), nullable=False), sa.Column("name", sa.String(200), nullable=False),
            sa.Column("session_count", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("weight", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("description", sa.Text()), sa.Column("learning_outcomes", sa.Text()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("code", name="uq_subjects_code"))
        op.create_index("ix_subjects_code", "subjects", ["code"], unique=True)

    if "program_subjects" not in tables:
        op.create_table("program_subjects",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("program_id", sa.Integer(), sa.ForeignKey("training_programs.id", ondelete="CASCADE"), nullable=False),
            sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.Column("prerequisite_subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="SET NULL")),
            sa.UniqueConstraint("program_id","subject_id", name="uq_program_subject"),
            sa.UniqueConstraint("program_id","order_index", name="uq_program_subject_order"))
        op.create_index("ix_program_subject_program_id", "program_subjects", ["program_id"])
        op.create_index("ix_program_subject_subject_id", "program_subjects", ["subject_id"])

    if "subject_sessions" not in tables:
        op.create_table("subject_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("sequence", sa.Integer(), nullable=False), sa.Column("topic", sa.String(255), nullable=False), sa.Column("objective", sa.Text()),
            sa.UniqueConstraint("subject_id","sequence", name="uq_subject_session_sequence"))
        op.create_index("ix_subject_sessions_subject_id", "subject_sessions", ["subject_id"])

    if "training_classes" not in tables:
        op.create_table("training_classes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("program_id", sa.Integer(), sa.ForeignKey("training_programs.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("name", sa.String(150), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="planned"))
        op.create_index("ix_training_classes_program_id", "training_classes", ["program_id"])
        op.create_index("ix_training_classes_status", "training_classes", ["status"])

    if "leads" not in tables:
        op.create_table("leads",
            sa.Column("id", sa.Integer(), primary_key=True), sa.Column("full_name", sa.String(150), nullable=False),
            sa.Column("phone", sa.String(30), nullable=False), sa.Column("email", sa.String(255)), sa.Column("source", sa.String(100)),
            sa.Column("interested_program_id", sa.Integer(), sa.ForeignKey("training_programs.id", ondelete="SET NULL")),
            sa.Column("status", sa.String(30), nullable=False, server_default="new"),
            sa.Column("assignee_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
            sa.Column("note", sa.Text()), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        for name, cols in [("ix_leads_full_name",["full_name"]),("ix_leads_phone",["phone"]),("ix_leads_source",["source"]),("ix_leads_status",["status"]),("ix_leads_assignee_user_id",["assignee_user_id"]),("ix_leads_created_at",["created_at"])]:
            op.create_index(name, "leads", cols)

    if "lead_assignment_history" not in tables:
        op.create_table("lead_assignment_history",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
            sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
            sa.Column("to_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        op.create_index("ix_lead_assignment_history_lead_id", "lead_assignment_history", ["lead_id"])


def downgrade():
    for table in ["lead_assignment_history","leads","subject_sessions","program_subjects","training_classes","subjects","training_programs"]:
        if table in _tables(op.get_bind()): op.drop_table(table)
    if "users" in _tables(op.get_bind()):
        cols=_cols(op.get_bind(),"users")
        for c in ["avatar_thumbnail_path","avatar_path","address","date_of_birth"]:
            if c in cols: op.drop_column("users", c)
