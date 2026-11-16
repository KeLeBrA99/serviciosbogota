"""
Migraciones de base de datos con Alembic.

`run_migrations()` se ejecuta al arrancar la API y deja la base en la última
versión. Para crear una migración después de cambiar un modelo:

    alembic revision --autogenerate -m "describe el cambio"
    # revisa el archivo generado en alembic/versions/ y súbelo al repo
"""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.db.database import engine

BACKEND_DIR = Path(__file__).resolve().parents[2]
BASELINE_REVISION = "0001"


def alembic_config() -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


def run_migrations() -> None:
    config = alembic_config()
    tables = set(inspect(engine).get_table_names())
    if "users" in tables and "alembic_version" not in tables:
        # Base creada antes de Alembic (con create_all): ya tiene el esquema
        # inicial, así que se marca como aplicado en vez de volver a crearlo.
        command.stamp(config, BASELINE_REVISION)
    command.upgrade(config, "head")
