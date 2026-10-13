"""Sprint 3 admissions funnel, students, classes and rooms.

Revision ID: 20261013_0003
Revises: 20261006_0002
Create Date: 2026-10-13
"""
from alembic import op
import sqlalchemy as sa

revision = "20261013_0003"
down_revision = "20261006_0002"
branch_labels = None
depends_on = None


def _tables(bind):
    return set(sa.inspect(bind).get_table_names())


def _cols(bind, table):
    return {x["name"] for x in sa.inspect(bind).get_columns(table)}


def _indexes(bind, table):
    return {x["name"] for x in sa.inspect(bind).get_indexes(table)}


def upgrade():
    bind = op.get_bind()
    tables = _tables(bind)

    if "lead_status_history" not in tables:
        op.create_table(
            "lead_status_history",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
            sa.Column("from_status", sa.String(30), nullable=True),
            sa.Column("to_status", sa.String(30), nullable=False),
            sa.Column("reason", sa.String(255), nullable=True),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("changed_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_lead_status_history_lead_id", "lead_status_history", ["lead_id"])
        op.create_index("ix_lead_status_history_to_status", "lead_status_history", ["to_status"])
        op.create_index("ix_lead_status_history_changed_at", "lead_status_history", ["changed_at"])

    if "lead_interactions" not in tables:
        op.create_table(
            "lead_interactions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
            sa.Column("interaction_type", sa.String(20), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("occurred_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("reminder_at", sa.DateTime(), nullable=True),
            sa.Column("reminder_completed_at", sa.DateTime(), nullable=True),
            sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_lead_interactions_lead_id", "lead_interactions", ["lead_id"])
        op.create_index("ix_lead_interactions_occurred_at", "lead_interactions", ["occurred_at"])
        op.create_index("ix_lead_interactions_reminder_at", "lead_interactions", ["reminder_at"])

    if "student_profiles" not in tables:
        op.create_table(
            "student_profiles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("student_code", sa.String(30), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("source_lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True),
            sa.Column("entry_level", sa.String(255), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("student_code", name="uq_student_profiles_student_code"),
            sa.UniqueConstraint("user_id", name="uq_student_profiles_user_id"),
            sa.UniqueConstraint("source_lead_id", name="uq_student_profiles_source_lead_id"),
        )
        op.create_index("ix_student_profiles_student_code", "student_profiles", ["student_code"], unique=True)
        op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"], unique=True)

    if "training_rooms" not in tables:
        op.create_table(
            "training_rooms",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(50), nullable=False),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("room_type", sa.String(20), nullable=False, server_default="physical"),
            sa.Column("capacity", sa.Integer(), nullable=True),
            sa.Column("online_url", sa.String(500), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("code", name="uq_training_rooms_code"),
        )
        op.create_index("ix_training_rooms_code", "training_rooms", ["code"], unique=True)
        op.create_index("ix_training_rooms_room_type", "training_rooms", ["room_type"])
        op.create_index("ix_training_rooms_is_active", "training_rooms", ["is_active"])

    if "training_classes" in _tables(bind):
        cols = _cols(bind, "training_classes")
        additions = [
            ("code", sa.Column("code", sa.String(50), nullable=True)),
            ("expected_start_date", sa.Column("expected_start_date", sa.Date(), nullable=True)),
            ("max_students", sa.Column("max_students", sa.Integer(), nullable=False, server_default="30")),
            ("delivery_mode", sa.Column("delivery_mode", sa.String(20), nullable=False, server_default="offline")),
            ("room_id", sa.Column("room_id", sa.Integer(), nullable=True)),
            ("completed_sessions", sa.Column("completed_sessions", sa.Integer(), nullable=False, server_default="0")),
            ("created_by_user_id", sa.Column("created_by_user_id", sa.Integer(), nullable=True)),
            ("created_at", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))),
            ("updated_at", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))),
        ]
        for name, column in additions:
            if name not in cols:
                op.add_column("training_classes", column)
        # Existing Sprint 2 rows get a deterministic class code before uniqueness is added.
        op.execute("UPDATE training_classes SET code = CONCAT('LEGACY-', id) WHERE code IS NULL OR code = ''")
        indexes = _indexes(bind, "training_classes")
        if "ix_training_classes_code" not in indexes:
            op.create_index("ix_training_classes_code", "training_classes", ["code"], unique=True)
        if "ix_training_classes_expected_start_date" not in indexes:
            op.create_index("ix_training_classes_expected_start_date", "training_classes", ["expected_start_date"])
        if "ix_training_classes_room_id" not in indexes:
            op.create_index("ix_training_classes_room_id", "training_classes", ["room_id"])
        # MySQL supports adding these constraints after the columns exist.
        inspector = sa.inspect(bind)
        fk_names = {fk.get("name") for fk in inspector.get_foreign_keys("training_classes")}
        if "fk_training_classes_room_id" not in fk_names:
            op.create_foreign_key("fk_training_classes_room_id", "training_classes", "training_rooms", ["room_id"], ["id"], ondelete="SET NULL")
        if "fk_training_classes_created_by_user_id" not in fk_names:
            op.create_foreign_key("fk_training_classes_created_by_user_id", "training_classes", "users", ["created_by_user_id"], ["id"], ondelete="SET NULL")

    tables = _tables(bind)
    if "class_subjects" not in tables:
        op.create_table(
            "class_subjects",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("class_id", sa.Integer(), sa.ForeignKey("training_classes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.Column("prerequisite_subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True),
            sa.UniqueConstraint("class_id", "subject_id", name="uq_class_subject"),
            sa.UniqueConstraint("class_id", "order_index", name="uq_class_subject_order"),
        )
        op.create_index("ix_class_subjects_class_id", "class_subjects", ["class_id"])
        op.create_index("ix_class_subjects_subject_id", "class_subjects", ["subject_id"])

    if "class_enrollments" not in tables:
        op.create_table(
            "class_enrollments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("class_id", sa.Integer(), sa.ForeignKey("training_classes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("student_id", sa.Integer(), sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="active"),
            sa.Column("enrolled_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("enrolled_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.UniqueConstraint("class_id", "student_id", name="uq_class_enrollment"),
        )
        op.create_index("ix_class_enrollments_class_id", "class_enrollments", ["class_id"])
        op.create_index("ix_class_enrollments_student_id", "class_enrollments", ["student_id"])
        op.create_index("ix_class_enrollments_status", "class_enrollments", ["status"])

    if "class_subject_staff" not in tables:
        op.create_table(
            "class_subject_staff",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("class_subject_id", sa.Integer(), sa.ForeignKey("class_subjects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("staff_role", sa.String(20), nullable=False),
            sa.Column("assigned_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("assigned_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.UniqueConstraint("class_subject_id", "user_id", "staff_role", name="uq_class_subject_staff"),
        )
        op.create_index("ix_class_subject_staff_class_subject_id", "class_subject_staff", ["class_subject_id"])
        op.create_index("ix_class_subject_staff_user_id", "class_subject_staff", ["user_id"])
        op.create_index("ix_class_subject_staff_staff_role", "class_subject_staff", ["staff_role"])


def downgrade():
    bind = op.get_bind()
    for table in ["class_subject_staff", "class_enrollments", "class_subjects"]:
        if table in _tables(bind):
            op.drop_table(table)

    if "training_classes" in _tables(bind):
        fk_names = {fk.get("name") for fk in sa.inspect(bind).get_foreign_keys("training_classes")}
        for name in ["fk_training_classes_created_by_user_id", "fk_training_classes_room_id"]:
            if name in fk_names:
                op.drop_constraint(name, "training_classes", type_="foreignkey")
        indexes = _indexes(bind, "training_classes")
        for index_name in ["ix_training_classes_room_id", "ix_training_classes_expected_start_date", "ix_training_classes_code"]:
            if index_name in indexes:
                op.drop_index(index_name, table_name="training_classes")
        cols = _cols(bind, "training_classes")
        for col in ["updated_at", "created_at", "created_by_user_id", "completed_sessions", "room_id", "delivery_mode", "max_students", "expected_start_date", "code"]:
            if col in cols:
                op.drop_column("training_classes", col)

    for table in ["training_rooms", "student_profiles", "lead_interactions", "lead_status_history"]:
        if table in _tables(bind):
            op.drop_table(table)
