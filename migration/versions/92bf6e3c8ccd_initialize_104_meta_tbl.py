"""Initialize 104 meta tbl

Revision ID: 92bf6e3c8ccd
Revises: 
Create Date: 2026-09-09 15:11:53.868350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '92bf6e3c8ccd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    detail_status_enum = postgresql.ENUM(
        "pending", "done", "failed",
        name="detail_status_enum"
    )
    detail_status_enum.create(op.get_bind())

    op.create_table(
        "meta_104_jobs",
        sa.Column("source_job_id", sa.String(32), primary_key=True),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("raw_location", sa.String(255), nullable=True),
        sa.Column("experience", sa.Integer(), nullable=True),
        sa.Column("remote", sa.SmallInteger(), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column(
            "detail_status",
            postgresql.ENUM(
                "pending", "done", "failed",
                name="detail_status_enum",
                create_type=False,   # ← key change: don't auto-create, it already exists
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_meta_104_jobs_updated_at
        BEFORE UPDATE ON meta_104_jobs
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("meta_104_jobs")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at() CASCADE;")
