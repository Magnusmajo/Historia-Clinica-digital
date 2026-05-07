from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config import get_settings
from app.database import Base

from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.clinical_note import ClinicalNote
from app.models.consultation import Consultation
from app.models.implant_area import ImplantArea
from app.models.module_record import ModuleRecord
from app.models.patient import Patient
from app.models.patient_photo import PatientPhoto
from app.models.user import User

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    return get_settings().database_url


def get_connect_args():
    settings = get_settings()
    options = [
        f"-c statement_timeout={settings.statement_timeout_ms}",
        "-c idle_in_transaction_session_timeout=30000",
    ]
    if settings.db_schema:
        options.append(f"-c search_path={settings.db_schema}")
    return {
        "connect_timeout": settings.connect_timeout,
        "options": " ".join(options),
        "application_name": "historia_clinica_migrations",
    }


def run_migrations_offline():
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(
        get_url(),
        connect_args=get_connect_args(),
        hide_parameters=True,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
