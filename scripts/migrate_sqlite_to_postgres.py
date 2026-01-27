#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
Migrates data from SQLite database to PostgreSQL

Usage:
    python migrate_sqlite_to_postgres.py --sqlite-url "sqlite:///./mediaflow.db" --postgres-url "postgresql://user:pass@localhost/mediaflow"

Requirements:
    pip install sqlalchemy psycopg2-binary aiosqlite
"""

import argparse
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Tables to migrate in order (respecting foreign key dependencies)
TABLES_ORDER = [
    "voice_settings",
    "categories",
    "music_tracks",
    "ai_clients",
    "client_configs",
    "message_templates",
    "shortcuts",
    "audio_messages",
    "schedules",
    "schedule_logs",
    "player_status",
]


def get_table_data(engine, table_name):
    """Get all data from a table"""
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name}"))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
    return columns, rows


def migrate_table(sqlite_engine, postgres_engine, table_name):
    """Migrate a single table from SQLite to PostgreSQL"""
    print(f"  Migrating table: {table_name}")

    # Check if table exists in source
    inspector = inspect(sqlite_engine)
    if table_name not in inspector.get_table_names():
        print(f"    Skipping: table does not exist in source")
        return 0

    columns, rows = get_table_data(sqlite_engine, table_name)

    if not rows:
        print(f"    Skipping: no data to migrate")
        return 0

    # Build insert statement
    column_list = ", ".join(columns)
    value_placeholders = ", ".join([f":{col}" for col in columns])
    insert_sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({value_placeholders})"

    # Insert into PostgreSQL
    with postgres_engine.begin() as conn:
        for row in rows:
            # Convert any None datetime to current time if needed
            for key, value in row.items():
                if value is None and key in ('created_at', 'updated_at'):
                    row[key] = datetime.utcnow()

            try:
                conn.execute(text(insert_sql), row)
            except Exception as e:
                print(f"    Error inserting row: {e}")
                print(f"    Row data: {row}")
                raise

    print(f"    Migrated {len(rows)} rows")
    return len(rows)


def reset_sequences(postgres_engine):
    """Reset PostgreSQL sequences to max(id) + 1"""
    print("\nResetting sequences...")

    sequences_sql = """
    SELECT sequence_name
    FROM information_schema.sequences
    WHERE sequence_schema = 'public'
    """

    with postgres_engine.connect() as conn:
        result = conn.execute(text(sequences_sql))
        sequences = [row[0] for row in result.fetchall()]

        for seq in sequences:
            # Extract table name from sequence (format: tablename_id_seq)
            table_name = seq.replace('_id_seq', '')

            try:
                # Get max id from table
                max_result = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}"))
                max_id = max_result.scalar()

                # Reset sequence
                conn.execute(text(f"SELECT setval('{seq}', {max_id + 1}, false)"))
                print(f"  Reset {seq} to {max_id + 1}")
            except Exception as e:
                print(f"  Could not reset {seq}: {e}")


def verify_migration(sqlite_engine, postgres_engine):
    """Verify row counts match between databases"""
    print("\nVerifying migration...")

    inspector = inspect(sqlite_engine)
    source_tables = inspector.get_table_names()

    all_match = True
    for table in TABLES_ORDER:
        if table not in source_tables:
            continue

        with sqlite_engine.connect() as conn:
            source_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()

        with postgres_engine.connect() as conn:
            dest_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()

        status = "OK" if source_count == dest_count else "MISMATCH"
        print(f"  {table}: {source_count} -> {dest_count} [{status}]")

        if source_count != dest_count:
            all_match = False

    return all_match


def main():
    parser = argparse.ArgumentParser(description='Migrate SQLite to PostgreSQL')
    parser.add_argument('--sqlite-url', required=True, help='SQLite database URL')
    parser.add_argument('--postgres-url', required=True, help='PostgreSQL database URL')
    parser.add_argument('--skip-verify', action='store_true', help='Skip verification step')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without executing')

    args = parser.parse_args()

    # Remove async prefix if present (for sync engine)
    sqlite_url = args.sqlite_url.replace('+aiosqlite', '')
    postgres_url = args.postgres_url.replace('+asyncpg', '')

    print(f"MediaFlow SQLite to PostgreSQL Migration")
    print(f"========================================")
    print(f"Source: {sqlite_url}")
    print(f"Target: {postgres_url}")
    print()

    if args.dry_run:
        print("DRY RUN - No changes will be made")
        print()

    # Create engines
    sqlite_engine = create_engine(sqlite_url)
    postgres_engine = create_engine(postgres_url)

    # Check source database
    print("Checking source database...")
    inspector = inspect(sqlite_engine)
    source_tables = inspector.get_table_names()
    print(f"  Found {len(source_tables)} tables: {', '.join(source_tables)}")

    if args.dry_run:
        print("\nDry run complete. Use without --dry-run to execute migration.")
        return

    # Migrate each table
    print("\nMigrating data...")
    total_rows = 0
    for table in TABLES_ORDER:
        try:
            rows = migrate_table(sqlite_engine, postgres_engine, table)
            total_rows += rows
        except Exception as e:
            print(f"  ERROR migrating {table}: {e}")
            sys.exit(1)

    print(f"\nTotal rows migrated: {total_rows}")

    # Reset sequences
    reset_sequences(postgres_engine)

    # Verify migration
    if not args.skip_verify:
        if verify_migration(sqlite_engine, postgres_engine):
            print("\nMigration completed successfully!")
        else:
            print("\nMigration completed with warnings - please verify data manually")
    else:
        print("\nMigration completed (verification skipped)")


if __name__ == "__main__":
    main()
