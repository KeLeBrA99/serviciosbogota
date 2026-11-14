"""Entorno de Alembic: usa el motor y los modelos de la aplicación."""
from alembic import context

from app import models  # noqa: F401  (registra todas las tablas en Base.metadata)
from app.db.database import Base, engine

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera SQL sin conectarse:  alembic upgrade head --sql"""
    context.configure(
        url=engine.url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
