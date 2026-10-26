"""initial schema

Revision ID: 001
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "barbers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "barber_schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("barber_id", sa.Integer(), sa.ForeignKey("barbers.id"), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
    )
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_code", sa.String(12), nullable=False),
        sa.Column("guest_name", sa.String(120), nullable=False),
        sa.Column("guest_phone", sa.String(32), nullable=False),
        sa.Column("guest_email", sa.String(120), nullable=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("barber_id", sa.Integer(), sa.ForeignKey("barbers.id"), nullable=True),
        sa.Column("any_barber", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "confirmed",
                "declined",
                "cancelled",
                "completed",
                name="appointmentstatus",
            ),
            nullable=False,
        ),
        sa.Column("revenue", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_appointments_booking_code", "appointments", ["booking_code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_appointments_booking_code", table_name="appointments")
    op.drop_table("appointments")
    op.drop_table("barber_schedules")
    op.drop_table("barbers")
    op.drop_table("services")
    op.execute("DROP TYPE IF EXISTS appointmentstatus")
