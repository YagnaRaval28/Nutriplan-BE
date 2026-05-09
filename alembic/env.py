from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.config import settings

# Import all models so autogenerate detects them
from app.db.session import Base
import app.models.user  # noqa: F401
import app.models.food  # noqa: F401
import app.models.diet_plan  # noqa: F401
import app.models.ai_recipe  # noqa: F401
import app.models.report  # noqa: F401
import app.models.message  # noqa: F401
import app.models.payment  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
