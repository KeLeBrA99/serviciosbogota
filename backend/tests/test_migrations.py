from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect, text

from app.db.database import Base, engine
from app.db.migrations import run_migrations
from tests.conftest import reset_database


def _current_revision():
    with engine.connect() as conn:
        return conn.execute(text("SELECT version_num FROM alembic_version")).scalar()


def _schema_diff():
    with engine.connect() as conn:
        return compare_metadata(MigrationContext.configure(conn), Base.metadata)


def test_migrations_build_the_same_schema_as_the_models():
    """Si alguien cambia un modelo sin crear su migración, esta prueba falla."""
    reset_database()
    run_migrations()
    assert _schema_diff() == []
    assert _current_revision() is not None


def test_existing_database_is_stamped_not_recreated():
    """Producción ya tiene las tablas (create_all): no deben recrearse ni perder datos."""
    reset_database()
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO categories (name, slug, icon) VALUES ('Prueba', 'prueba', 'x')"))

    run_migrations()

    assert "alembic_version" in inspect(engine).get_table_names()
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM categories")).scalar() == 1
    run_migrations()  # volver a arrancar no cambia nada
    assert _schema_diff() == []
