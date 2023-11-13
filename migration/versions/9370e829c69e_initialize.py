"""initialize

Revision ID: 9370e829c69e
Revises: 
Create Date: 2023-11-13 13:47:21.205217
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "9370e829c69e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    op.create_table(
        "account",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("fullname", sa.String(length=128), nullable=False),
        sa.Column("introduction", sa.Text(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account")),
        sa.UniqueConstraint(
            "username", name=op.f("uq_ecac4fd2482f5973957e2c34170363a9")
        ),
    )
    op.create_index(
        op.f("ix_4e185986f4bd55eca3ceb40991519a4c"),
        "account",
        ["created"],
        unique=False,
    )
    op.create_table(
        "daily_log",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_log")),
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
        "account_login",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("ipaddr", sa.String(), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["account.id"],
            name=op.f("fk_6009890ca2935812870320d3ec76e759"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account_login")),
    )
    op.create_index(
        op.f("ix_4af6b6ab96a5501198b5b3ab0b29618e"),
        "account_login",
        ["created"],
        unique=False,
    )
    op.create_index(
        op.f("ix_bc6521d9e2af583b86e0f51e267d99cd"),
        "account_login",
        ["account_id", "created"],
        unique=False,
    )
    op.create_table(
        "exercise_log",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("exercise_type", sa.String(), nullable=False),
        sa.Column("daily_log_id", sa.UUID(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["daily_log_id"],
            ["daily_log.id"],
            name=op.f("fk_ba71015049d85421b65a2d2665cca716"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercise_log")),
    )
    op.create_index(
        "ExerciseLog.daily_log_id",
        "exercise_log",
        ["exercise_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_856512e4d082509bb6c51ccc79b12a0f"),
        "exercise_log",
        ["created"],
        unique=False,
    )
    op.create_table(
        "performance_log",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("performance_count", sa.Integer(), nullable=False),
        sa.Column("exercise_log_id", sa.UUID(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["exercise_log_id"],
            ["exercise_log.id"],
            name=op.f("fk_51e4b81518c453b4889ddbedc11394de"),
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
        op.f("ix_856512e4d082509bb6c51ccc79b12a0f"), table_name="exercise_log"
    )
    op.drop_index(
        "ExerciseLog.daily_log_id", table_name="exercise_log", postgresql_using="gin"
    )
    op.drop_table("exercise_log")
    op.drop_index(
        op.f("ix_bc6521d9e2af583b86e0f51e267d99cd"), table_name="account_login"
    )
    op.drop_index(
        op.f("ix_4af6b6ab96a5501198b5b3ab0b29618e"), table_name="account_login"
    )
    op.drop_table("account_login")
    op.drop_index(op.f("ix_22f73e559bc8574381ce473cef656c28"), table_name="daily_log")
    op.drop_index(op.f("ix_17840f910dc058349b16f89d9bed53fa"), table_name="daily_log")
    op.drop_table("daily_log")
    op.drop_index(op.f("ix_4e185986f4bd55eca3ceb40991519a4c"), table_name="account")
    op.drop_table("account")
    # ### end Alembic commands ###
