"""Esquema inicial: las seis tablas tal como estaban antes de usar Alembic.

En una base que ya tenía las tablas (producción) esta migración no se ejecuta:
la aplicación la marca como aplicada al arrancar (ver app/db/migrations.py).

Revision ID: 0001
Revises: 
Create Date: 2026-11-14 11:12:55.675901
"""
from alembic import op
import sqlalchemy as sa


revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('icon', sa.String(length=10), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_categories_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_categories_slug'), ['slug'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=150), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('role', sa.Enum('admin', 'business_owner', name='userrole'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_id'), ['id'], unique=False)

    op.create_table('businesses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('short_description', sa.String(length=300), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('whatsapp', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('website', sa.String(length=300), nullable=True),
    sa.Column('localidad', sa.String(length=100), nullable=False),
    sa.Column('address', sa.String(length=300), nullable=True),
    sa.Column('neighborhood', sa.String(length=150), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('logo_url', sa.String(length=500), nullable=True),
    sa.Column('cover_url', sa.String(length=500), nullable=True),
    sa.Column('photos', sa.JSON(), nullable=True),
    sa.Column('tags', sa.JSON(), nullable=True),
    sa.Column('amenities', sa.JSON(), nullable=True),
    sa.Column('service_areas', sa.JSON(), nullable=True),
    sa.Column('schedule', sa.JSON(), nullable=True),
    sa.Column('rating_avg', sa.Float(), nullable=True),
    sa.Column('rating_count', sa.Integer(), nullable=True),
    sa.Column('view_count', sa.Integer(), nullable=True),
    sa.Column('contact_count', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'active', 'suspended', 'rejected', name='businessstatus'), nullable=True),
    sa.Column('is_featured', sa.Boolean(), nullable=True),
    sa.Column('is_open_now', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('businesses', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_businesses_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_businesses_localidad'), ['localidad'], unique=False)
        batch_op.create_index(batch_op.f('ix_businesses_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_businesses_slug'), ['slug'], unique=True)

    op.create_table('contact_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('client_name', sa.String(length=100), nullable=False),
    sa.Column('client_phone', sa.String(length=20), nullable=True),
    sa.Column('client_email', sa.String(length=255), nullable=True),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('service_requested', sa.String(length=200), nullable=True),
    sa.Column('status', sa.Enum('new', 'seen', 'replied', name='contactstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('contact_requests', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_contact_requests_id'), ['id'], unique=False)

    op.create_table('reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('author_name', sa.String(length=100), nullable=False),
    sa.Column('rating', sa.Float(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('response', sa.Text(), nullable=True),
    sa.Column('is_approved', sa.Boolean(), nullable=True),
    sa.Column('is_flagged', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reviews_id'), ['id'], unique=False)

    op.create_table('subscriptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('plan', sa.Enum('basic', 'premium', name='plantype'), nullable=False),
    sa.Column('status', sa.Enum('active', 'expired', 'cancelled', 'pending_payment', name='subscriptionstatus'), nullable=True),
    sa.Column('wompi_transaction_id', sa.String(length=200), nullable=True),
    sa.Column('wompi_subscription_id', sa.String(length=200), nullable=True),
    sa.Column('amount_cop', sa.Float(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('business_id')
    )
    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_subscriptions_id'), ['id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('subscriptions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_subscriptions_id'))

    op.drop_table('subscriptions')
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reviews_id'))

    op.drop_table('reviews')
    with op.batch_alter_table('contact_requests', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_contact_requests_id'))

    op.drop_table('contact_requests')
    with op.batch_alter_table('businesses', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_businesses_slug'))
        batch_op.drop_index(batch_op.f('ix_businesses_name'))
        batch_op.drop_index(batch_op.f('ix_businesses_localidad'))
        batch_op.drop_index(batch_op.f('ix_businesses_id'))

    op.drop_table('businesses')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_id'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_categories_slug'))
        batch_op.drop_index(batch_op.f('ix_categories_id'))

    op.drop_table('categories')
