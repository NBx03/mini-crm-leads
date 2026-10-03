import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect():
    # prepare_threshold=None: пулер Neon работает в режиме transaction и не поддерживает prepared statements.
    return psycopg.connect(
        os.environ["DATABASE_URL"],
        row_factory=dict_row,
        prepare_threshold=None,
    )


def init_schema():
    with connect() as conn:
        conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
