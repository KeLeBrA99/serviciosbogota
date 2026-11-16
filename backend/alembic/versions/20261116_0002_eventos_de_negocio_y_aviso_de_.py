"""eventos de negocio y aviso de vencimiento

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-16 18:53:52.548480
"""
from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('business_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('business_events', schema=None) as batch_op:
        batch_op.create_index('ix_business_events_business_created', ['business_id', 'created_at'], unique=False)

    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expiry_notified_at', sa.DateTime(timezone=True), nullable=True))



def downgrade() -> None:
    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.drop_column('expiry_notified_at')

    with op.batch_alter_table('business_events', schema=None) as batch_op:
        batch_op.drop_index('ix_business_events_business_created')

    op.drop_table('business_events')
