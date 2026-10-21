"""Sprint 4 timetable and attendance.

Revision ID: 20261013_0004
Revises: 20261013_0003
Create Date: 2026-10-13
"""
from alembic import op
import sqlalchemy as sa

revision = "20261013_0004"
down_revision = "20261013_0003"
branch_labels = None
depends_on = None


def _tables(bind):
    return set(sa.inspect(bind).get_table_names())


def upgrade():
    bind=op.get_bind(); tables=_tables(bind)
    if "academic_holidays" not in tables:
        op.create_table("academic_holidays",
            sa.Column("id",sa.Integer(),primary_key=True),
            sa.Column("holiday_date",sa.Date(),nullable=False,unique=True),
            sa.Column("name",sa.String(200),nullable=False),
            sa.Column("created_by_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),
            sa.Column("created_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")),)
        op.create_index("ix_academic_holidays_holiday_date","academic_holidays",["holiday_date"],unique=True)
    if "class_schedule_sessions" not in tables:
        op.create_table("class_schedule_sessions",
            sa.Column("id",sa.Integer(),primary_key=True),
            sa.Column("class_id",sa.Integer(),sa.ForeignKey("training_classes.id",ondelete="CASCADE"),nullable=False),
            sa.Column("class_subject_id",sa.Integer(),sa.ForeignKey("class_subjects.id",ondelete="CASCADE"),nullable=False),
            sa.Column("subject_session_id",sa.Integer(),sa.ForeignKey("subject_sessions.id",ondelete="RESTRICT"),nullable=False),
            sa.Column("start_at",sa.DateTime(),nullable=False),sa.Column("end_at",sa.DateTime(),nullable=False),
            sa.Column("room_id",sa.Integer(),sa.ForeignKey("training_rooms.id",ondelete="SET NULL"),nullable=True),
            sa.Column("teacher_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),
            sa.Column("status",sa.String(20),nullable=False,server_default="scheduled"),
            sa.Column("cancellation_reason",sa.String(500),nullable=True),
            sa.Column("conflict_override",sa.Boolean(),nullable=False,server_default=sa.false()),
            sa.Column("created_by_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),
            sa.Column("created_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("class_id","subject_session_id",name="uq_class_schedule_lesson"),)
        for col in ["class_id","class_subject_id","subject_session_id","start_at","end_at","room_id","teacher_user_id","status"]:
            op.create_index(f"ix_class_schedule_sessions_{col}","class_schedule_sessions",[col])
    if "schedule_change_history" not in tables:
        op.create_table("schedule_change_history",
            sa.Column("id",sa.Integer(),primary_key=True),
            sa.Column("schedule_session_id",sa.Integer(),sa.ForeignKey("class_schedule_sessions.id",ondelete="CASCADE"),nullable=False),
            sa.Column("action",sa.String(30),nullable=False),sa.Column("old_start_at",sa.DateTime(),nullable=True),sa.Column("old_end_at",sa.DateTime(),nullable=True),
            sa.Column("old_room_id",sa.Integer(),nullable=True),sa.Column("old_teacher_user_id",sa.Integer(),nullable=True),sa.Column("reason",sa.String(500),nullable=True),
            sa.Column("actor_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),sa.Column("changed_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")),)
        op.create_index("ix_schedule_change_history_schedule_session_id","schedule_change_history",["schedule_session_id"])
    if "user_notifications" not in tables:
        op.create_table("user_notifications",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("title",sa.String(200),nullable=False),sa.Column("message",sa.Text(),nullable=False),sa.Column("link",sa.String(500),nullable=True),sa.Column("read_at",sa.DateTime(),nullable=True),sa.Column("created_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")))
        op.create_index("ix_user_notifications_user_id","user_notifications",["user_id"])
    if "student_status_history" not in tables:
        op.create_table("student_status_history",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("student_id",sa.Integer(),sa.ForeignKey("student_profiles.id",ondelete="CASCADE"),nullable=False),sa.Column("action",sa.String(30),nullable=False),sa.Column("from_class_id",sa.Integer(),sa.ForeignKey("training_classes.id",ondelete="SET NULL"),nullable=True),sa.Column("to_class_id",sa.Integer(),sa.ForeignKey("training_classes.id",ondelete="SET NULL"),nullable=True),sa.Column("effective_date",sa.Date(),nullable=False),sa.Column("reason",sa.String(500),nullable=False),sa.Column("actor_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),sa.Column("created_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")))
        op.create_index("ix_student_status_history_student_id","student_status_history",["student_id"])
        op.create_index("ix_student_status_history_effective_date","student_status_history",["effective_date"])
    if "attendance_records" not in tables:
        op.create_table("attendance_records",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("schedule_session_id",sa.Integer(),sa.ForeignKey("class_schedule_sessions.id",ondelete="CASCADE"),nullable=False),sa.Column("student_id",sa.Integer(),sa.ForeignKey("student_profiles.id",ondelete="CASCADE"),nullable=False),sa.Column("status",sa.String(30),nullable=False),sa.Column("note",sa.String(500),nullable=True),sa.Column("marked_by_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),sa.Column("marked_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")),sa.Column("updated_by_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),sa.Column("updated_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")),sa.UniqueConstraint("schedule_session_id","student_id",name="uq_attendance_session_student"))
        op.create_index("ix_attendance_records_schedule_session_id","attendance_records",["schedule_session_id"])
        op.create_index("ix_attendance_records_student_id","attendance_records",["student_id"])
    if "attendance_audit_logs" not in tables:
        op.create_table("attendance_audit_logs",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("attendance_id",sa.Integer(),sa.ForeignKey("attendance_records.id",ondelete="CASCADE"),nullable=False),sa.Column("from_status",sa.String(30),nullable=True),sa.Column("to_status",sa.String(30),nullable=False),sa.Column("reason",sa.String(500),nullable=True),sa.Column("actor_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),sa.Column("changed_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")))
        op.create_index("ix_attendance_audit_logs_attendance_id","attendance_audit_logs",["attendance_id"])
    if "absence_requests" not in tables:
        op.create_table("absence_requests",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("schedule_session_id",sa.Integer(),sa.ForeignKey("class_schedule_sessions.id",ondelete="CASCADE"),nullable=False),sa.Column("student_id",sa.Integer(),sa.ForeignKey("student_profiles.id",ondelete="CASCADE"),nullable=False),sa.Column("reason",sa.Text(),nullable=False),sa.Column("evidence_path",sa.String(500),nullable=True),sa.Column("status",sa.String(20),nullable=False,server_default="pending"),sa.Column("reviewer_user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL"),nullable=True),sa.Column("review_reason",sa.String(500),nullable=True),sa.Column("created_at",sa.DateTime(),nullable=False,server_default=sa.text("CURRENT_TIMESTAMP")),sa.Column("reviewed_at",sa.DateTime(),nullable=True))
        op.create_index("ix_absence_requests_schedule_session_id","absence_requests",["schedule_session_id"])
        op.create_index("ix_absence_requests_student_id","absence_requests",["student_id"])
        op.create_index("ix_absence_requests_status","absence_requests",["status"])


def downgrade():
    bind=op.get_bind()
    for table in ["absence_requests","attendance_audit_logs","attendance_records","student_status_history","user_notifications","schedule_change_history","class_schedule_sessions","academic_holidays"]:
        if table in _tables(bind): op.drop_table(table)
