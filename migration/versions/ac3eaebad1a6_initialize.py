"""initialize

Revision ID: ac3eaebad1a6
Revises: 
Create Date: 2023-11-17 21:08:28.183028
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "ac3eaebad1a6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "daily_log",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_log")),
        sa.UniqueConstraint("date", name=op.f("uq_17840f910dc058349b16f89d9bed53fa")),
    )
    op.create_index(
        op.f("ix_17840f910dc058349b16f89d9bed53fa"), "daily_log", ["date"], unique=False
    )
    op.create_index(
        op.f("ix_22f73e559bc8574381ce473cef656c28"),
        "daily_log",
        ["created"],
        unique=False,
    )
    op.create_table(
        "exercise_category",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercise_category")),
    )
    op.create_index(
        op.f("ix_0bc174c5ac195545a69acf340d291600"),
        "exercise_category",
        ["created"],
        unique=False,
    )
    op.create_table(
        "performance_log",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("exercise_category_id", sa.UUID(), nullable=False),
        sa.Column("daily_log_id", sa.UUID(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["daily_log_id"],
            ["daily_log.id"],
            name=op.f("fk_9ba7d5df68045bb1810c5c3acf16d11a"),
        ),
        sa.ForeignKeyConstraint(
            ["exercise_category_id"],
            ["exercise_category.id"],
            name=op.f("fk_031573a496b95e7096be4e829232e994"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_performance_log")),
    )
    op.create_index(
        op.f("ix_e4d2e328a8045e468623c0b2a253996c"),
        "performance_log",
        ["created"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_index(
        op.f("ix_e4d2e328a8045e468623c0b2a253996c"), table_name="performance_log"
    )
    op.drop_table("performance_log")
    op.drop_index(
        op.f("ix_0bc174c5ac195545a69acf340d291600"), table_name="exercise_category"
    )
    op.drop_table("exercise_category")
    op.drop_index(op.f("ix_22f73e559bc8574381ce473cef656c28"), table_name="daily_log")
    op.drop_index(op.f("ix_17840f910dc058349b16f89d9bed53fa"), table_name="daily_log")
    op.drop_table("daily_log")
    # ### end Alembic commands ###
