#!/usr/bin/env python3
"""
Restore a Postgres dump file into the database described by `api/.env`.

Features:
- Detects dump type (custom/pg_restore vs plain SQL) using the `file` command.
- Supports a safe dry-run mode that prints the commands without running them.
- Optionally drops & recreates the target database before restoring (`--drop-create`).
- Uses `PGPASSWORD` from the env for non-interactive password passing.

Usage (from project root):
  python3 -m api.scripts.restore_from_dump /path/to/dump.dump
  python3 -m api.scripts.restore_from_dump /path/to/dump.dump --apply --yes
  python3 -m api.scripts.restore_from_dump /path/to/dump.sql --drop-create --apply --yes

Caveats:
- `file` and `pg_restore` / `psql` must be available in PATH.
- Dropping and creating a database requires sufficient privileges.
"""
import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv

# Ensure api/ on sys.path when running as module
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.dirname(SCRIPT_DIR)
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

# Load api/.env if present
env_path = os.path.join(API_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

PSQL_HOST = os.getenv('PSQL_HOST', 'localhost')
PSQL_PORT = os.getenv('PSQL_PORT', '5432')
PSQL_DB = os.getenv('PSQL_DB', '')
PSQL_USER = os.getenv('PSQL_USER', '')
PSQL_PASSWORD = os.getenv('PSQL_PASSWORD', '')

if not PSQL_DB or not PSQL_USER:
    print('Error: PSQL_DB and PSQL_USER must be set in api/.env (or environment)')
    sys.exit(1)


def detect_dump_type(path: str) -> str:
    """Return 'custom' for pg_restore custom format, otherwise 'plain'."""
    try:
        res = subprocess.run(['file', path], capture_output=True, text=True, check=True)
        out = res.stdout.lower()
        if 'postgresql' in out and 'custom' in out:
            return 'custom'
    except Exception:
        # If file command not available or fails, fall back to checking extension
        pass
    # fallback based on extension
    if path.endswith('.dump') or path.endswith('.pgdump') or path.endswith('.dump.gz'):
        return 'custom'
    return 'plain'


def run_cmd(cmd, env=None, dry_run=True):
    print('COMMAND:', ' '.join(cmd))
    if dry_run:
        return 0
    return subprocess.run(cmd, check=True, env=env)


def make_env():
    env = os.environ.copy()
    if PSQL_PASSWORD:
        env['PGPASSWORD'] = PSQL_PASSWORD
    return env


def main():
    p = argparse.ArgumentParser()
    p.add_argument('dump', help='Path to dump file (custom or plain SQL)')
    p.add_argument('--drop-create', action='store_true', help='Drop and recreate the target database before restore')
    p.add_argument('--apply', action='store_true', help='Perform the restore (default is dry-run)')
    p.add_argument('--yes', action='store_true', help='Auto-confirm dangerous actions')
    args = p.parse_args()

    dump_path = args.dump
    if not os.path.exists(dump_path):
        print('Error: dump file not found:', dump_path)
        sys.exit(1)

    if args.drop_create and args.apply and not args.yes:
        confirm = input('This will DROP and RECREATE the database "{}". Type YES to continue: '.format(PSQL_DB))
        if confirm != 'YES':
            print('Aborting.')
            return

    dry_run = not args.apply
    dump_type = detect_dump_type(dump_path)
    print(f'Detected dump type: {dump_type}')

    env = make_env()

    # Optionally drop & recreate the DB
    if args.drop_create:
        # Use the postgres database (or template1) as connection target
        drop_cmd = [
            'psql',
            '-h', PSQL_HOST,
            '-p', str(PSQL_PORT),
            '-U', PSQL_USER,
            '-d', 'postgres',
            '-c', f"DROP DATABASE IF EXISTS \"{PSQL_DB}\"; CREATE DATABASE \"{PSQL_DB}\";"
        ]
        run_cmd(drop_cmd, env=env, dry_run=dry_run)

    if dump_type == 'custom':
        # Use pg_restore. Place flags in correct order so values aren't shifted.
        restore_cmd = [
            'pg_restore',
            '--host', PSQL_HOST,
            '--port', str(PSQL_PORT),
            '--username', PSQL_USER,
            '--dbname', PSQL_DB,
            '--clean',
            '--no-owner',
            '--verbose',
            dump_path,
        ]
        run_cmd(restore_cmd, env=env, dry_run=dry_run)
    else:
        # Plain SQL restore via psql
        restore_cmd = [
            'psql',
            '-h', PSQL_HOST,
            '-p', str(PSQL_PORT),
            '-U', PSQL_USER,
            '-d', PSQL_DB,
            '-f', dump_path
        ]
        run_cmd(restore_cmd, env=env, dry_run=dry_run)

    if dry_run:
        print('\nDry-run complete. To actually restore, re-run with --apply --yes')
    else:
        print('\nRestore completed.')


if __name__ == '__main__':
    main()
