"""add interest_rate, interest_type to debts + platform_rates table

Revision ID: 001
Revises: 
Create Date: 2026-06-11
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('debts', sa.Column('interest_rate', sa.Float(), nullable=True,
                  comment='Interest rate percentage, e.g. 2.5 = 2.5%'))
    op.add_column('debts', sa.Column('interest_type', sa.String(length=10), nullable=True,
                  comment='daily, monthly, yearly, flat'))
    op.create_table(
        'platform_rates',
        sa.Column('platform', sa.String(length=100), primary_key=True),
        sa.Column('avg_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('common_type', sa.String(length=10), nullable=True),
        sa.Column('sample_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('type_counts', sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('debts', 'interest_type')
    op.drop_column('debts', 'interest_rate')
    op.drop_table('platform_rates')
