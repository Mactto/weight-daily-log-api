"""first migration

Revision ID: 5d17f13c1cf9
Revises:
Create Date: 2023-06-29 14:55:27.917121
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "5d17f13c1cf9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "account",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("fullname", sa.String(length=128), nullable=False),
        sa.Column("introduction", sa.Text(), nullable=False),
        sa.Column(
            "tags",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "condition",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "effective_erns",
            postgresql.ARRAY(sa.Text()),
            sa.Computed(
                "ARRAY[('ern:library::account/' || id::text),'ern:library::/*']"
                "::text[]"
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account")),
        sa.UniqueConstraint(
            "username", name=op.f("uq_ecac4fd2482f5973957e2c34170363a9")
        ),
    )
    op.create_index(
        op.f("ix_119f75a37bae5293acb708df465b0ccb"),
        "account",
        ["effective_erns"],
        unique=False,
    )
    op.create_index(
        op.f("ix_317815a4e50551108a69f1855931f307"),
        "account",
        ["tags"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"tags": "jsonb_path_ops"},
    )
    op.create_index(
        op.f("ix_33753f04903551089db12c83ff10a544"),
        "account",
        ["condition"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"condition": "jsonb_path_ops"},
    )
    op.create_index(
        op.f("ix_4e185986f4bd55eca3ceb40991519a4c"),
        "account",
        ["created"],
        unique=False,
    )
    op.create_table(
        "account_login",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("ipaddr", sa.String(), nullable=False),
        sa.Column("account_id", sa.UUID(), nullable=False),
        sa.Column(
            "tags",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "condition",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "effective_erns",
            postgresql.ARRAY(sa.Text()),
            sa.Computed(
                "ARRAY[('ern:library::account_login/' || id::text),'ern:library::/*']"
                "::text[]"
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["account.id"],
            name=op.f("fk_6009890ca2935812870320d3ec76e759"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account_login")),
    )
    op.create_index(
        op.f("ix_224abedf864f5df0a69eed7a3a780612"),
        "account_login",
        ["effective_erns"],
        unique=False,
    )
    op.create_index(
        op.f("ix_4af6b6ab96a5501198b5b3ab0b29618e"),
        "account_login",
        ["created"],
        unique=False,
    )
    op.create_index(
        op.f("ix_5fe794de983454af96427a7bc59f177b"),
        "account_login",
        ["tags"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"tags": "jsonb_path_ops"},
    )
    op.create_index(
        op.f("ix_6b2fbf0222b9596f8d03afde493d9d66"),
        "account_login",
        ["condition"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"condition": "jsonb_path_ops"},
    )
    op.create_index(
        op.f("ix_bc6521d9e2af583b86e0f51e267d99cd"),
        "account_login",
        ["account_id", "created"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_bc6521d9e2af583b86e0f51e267d99cd"), table_name="account_login"
    )
    op.drop_index(
        op.f("ix_6b2fbf0222b9596f8d03afde493d9d66"),
        table_name="account_login",
        postgresql_using="gin",
        postgresql_ops={"condition": "jsonb_path_ops"},
    )
    op.drop_index(
        op.f("ix_5fe794de983454af96427a7bc59f177b"),
        table_name="account_login",
        postgresql_using="gin",
        postgresql_ops={"tags": "jsonb_path_ops"},
    )
    op.drop_index(
        op.f("ix_4af6b6ab96a5501198b5b3ab0b29618e"), table_name="account_login"
    )
    op.drop_index(
        op.f("ix_224abedf864f5df0a69eed7a3a780612"), table_name="account_login"
    )
    op.drop_table("account_login")
    op.drop_index(op.f("ix_4e185986f4bd55eca3ceb40991519a4c"), table_name="account")
    op.drop_index(
        op.f("ix_33753f04903551089db12c83ff10a544"),
        table_name="account",
        postgresql_using="gin",
        postgresql_ops={"condition": "jsonb_path_ops"},
    )
    op.drop_index(
        op.f("ix_317815a4e50551108a69f1855931f307"),
        table_name="account",
        postgresql_using="gin",
        postgresql_ops={"tags": "jsonb_path_ops"},
    )
    op.drop_index(op.f("ix_119f75a37bae5293acb708df465b0ccb"), table_name="account")
    op.drop_table("account")
