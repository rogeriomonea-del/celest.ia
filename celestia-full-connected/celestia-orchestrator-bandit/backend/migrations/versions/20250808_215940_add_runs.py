"""add runs table
Revision ID: 20250808_215940
Revises: 
Create Date: 2025-08-08T21:59:40.252073

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250808_215940"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source', sa.String(length=50), index=True),
        sa.Column('mode', sa.String(length=16), index=True),
        sa.Column('route', sa.String(length=31), index=True),
        sa.Column('ok', sa.Boolean(), default=False, index=True),
        sa.Column('latency_ms', sa.Integer(), default=0),
        sa.Column('fail_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('runs')
