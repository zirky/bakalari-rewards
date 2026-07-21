"""initial

Revision ID: 0001
Revises:
Create Date: 2026-07-21
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('parents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(64), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('children',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('parents.id'), nullable=False),
        sa.Column('lightning_address', sa.String(255)),
        sa.Column('auto_payout', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table('bakalari_accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('child_id', sa.Integer(), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('base_url', sa.String(255), nullable=False),
        sa.Column('username', sa.String(128), nullable=False),
        sa.Column('encrypted_password', sa.Text(), nullable=False),
    )
    op.create_table('grade_rules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('child_id', sa.Integer(), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=False),
        sa.Column('reward_czk', sa.Numeric(10, 2), nullable=False, default=0),
    )
    op.create_table('sync_runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('child_id', sa.Integer(), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('finished_at', sa.DateTime(timezone=True)),
        sa.Column('status', sa.String(32), default='running'),
        sa.Column('new_marks_count', sa.Integer(), default=0),
        sa.Column('error_message', sa.Text()),
    )
    op.create_table('marks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('child_id', sa.Integer(), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('sync_run_id', sa.Integer(), sa.ForeignKey('sync_runs.id')),
        sa.Column('subject', sa.String(128), nullable=False),
        sa.Column('mark_text', sa.String(16), nullable=False),
        sa.Column('mark_numeric', sa.Integer()),
        sa.Column('mark_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reward_czk', sa.Numeric(10, 2), default=0),
        sa.Column('processed', sa.Boolean(), default=False),
        sa.UniqueConstraint('child_id', 'subject', 'mark_text', 'mark_date', name='uq_mark_idempotent'),
    )
    op.create_table('balances',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('child_id', sa.Integer(), sa.ForeignKey('children.id'), nullable=False, unique=True),
        sa.Column('running_balance_czk', sa.Numeric(10, 2), default=0),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_table('payouts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('child_id', sa.Integer(), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('sync_run_id', sa.Integer(), sa.ForeignKey('sync_runs.id')),
        sa.Column('status', sa.String(32), default='pending'),
        sa.Column('amount_czk', sa.Numeric(10, 2), nullable=False),
        sa.Column('amount_sats', sa.Integer()),
        sa.Column('btc_czk_rate', sa.Numeric(16, 2)),
        sa.Column('lightning_address', sa.String(255)),
        sa.Column('payment_hash', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('paid_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text()),
    )
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('parents.id')),
        sa.Column('action', sa.String(128), nullable=False),
        sa.Column('detail', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for tbl in ['audit_logs','payouts','balances','marks','sync_runs','grade_rules','bakalari_accounts','children','parents']:
        op.drop_table(tbl)
