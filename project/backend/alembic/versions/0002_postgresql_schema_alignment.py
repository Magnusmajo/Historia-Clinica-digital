"""align PostgreSQL schema with production models

Revision ID: 0002_postgresql_schema_alignment
Revises: 0001_initial_schema
Create Date: 2026-05-07 18:15:00.000000
"""

from alembic import op

revision = "0002_postgresql_schema_alignment"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE audit_logs ALTER COLUMN details TYPE JSONB USING details::jsonb")
    op.execute("ALTER TABLE clinical_notes ALTER COLUMN notes TYPE JSONB USING notes::jsonb")
    op.execute("ALTER TABLE module_records ALTER COLUMN payload TYPE JSONB USING payload::jsonb")
    op.execute(
        "ALTER TABLE implant_areas ALTER COLUMN drawing_data TYPE JSONB "
        "USING drawing_data::jsonb"
    )

    op.execute("ALTER TABLE patients DROP CONSTRAINT IF EXISTS patients_ci_key")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key")
    op.drop_index("ix_patients_ci", table_name="patients", if_exists=True)
    op.drop_index("ix_users_email", table_name="users", if_exists=True)
    op.create_index("ix_patients_ci", "patients", ["ci"], unique=True, if_not_exists=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True, if_not_exists=True)


def downgrade():
    op.execute("ALTER TABLE audit_logs ALTER COLUMN details TYPE JSON USING details::json")
    op.execute("ALTER TABLE clinical_notes ALTER COLUMN notes TYPE JSON USING notes::json")
    op.execute("ALTER TABLE module_records ALTER COLUMN payload TYPE JSON USING payload::json")
    op.execute(
        "ALTER TABLE implant_areas ALTER COLUMN drawing_data TYPE JSON "
        "USING drawing_data::json"
    )

    op.drop_index("ix_users_email", table_name="users", if_exists=True)
    op.drop_index("ix_patients_ci", table_name="patients", if_exists=True)
    op.create_unique_constraint("patients_ci_key", "patients", ["ci"])
    op.create_unique_constraint("users_email_key", "users", ["email"])
    op.create_index("ix_patients_ci", "patients", ["ci"], unique=False, if_not_exists=True)
    op.create_index("ix_users_email", "users", ["email"], unique=False, if_not_exists=True)
