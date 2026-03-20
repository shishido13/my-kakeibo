from collections.abc import Generator
from contextlib import contextmanager
from datetime import date, datetime

import libsql_client

from app.core.config import settings


def _normalize_turso_url(database_url: str) -> str:
    return database_url.replace('libsql://', 'https://').replace('wss://', 'https://')


if not settings.DATABASE_URL:
    raise RuntimeError('DATABASE_URL is not configured.')

if not settings.TURSO_TOKEN:
    raise RuntimeError('TURSO_TOKEN is not configured.')

if 'turso.io' not in settings.DATABASE_URL and not settings.DATABASE_URL.startswith(('libsql://', 'wss://')):
    raise RuntimeError('This backend now supports Turso/libsql connections only.')

_client = libsql_client.create_client_sync(
    url=_normalize_turso_url(settings.DATABASE_URL),
    auth_token=settings.TURSO_TOKEN,
)


def _serialize_value(value):
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return '1' if value else '0'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        return f"'{value.isoformat(sep=' ')}'"
    if isinstance(value, date):
        return f"'{value.isoformat()}'"
    return "'{}'".format(str(value).replace("'", "''"))


class DatabaseSession:
    def __init__(self, client):
        self.client = client

    def fetch_all(self, sql: str):
        result = self.client.execute(sql)
        return [
            {column: row[index] for index, column in enumerate(result.columns)}
            for row in result.rows
        ]

    def fetch_one(self, sql: str):
        rows = self.fetch_all(sql)
        return rows[0] if rows else None

    def fetch_scalar(self, sql: str):
        row = self.fetch_one(sql)
        if not row:
            return None
        return next(iter(row.values()))

    def execute(self, sql: str):
        return self.client.execute(sql)

    def insert(self, table_name: str, values: dict):
        columns = [key for key, value in values.items() if value is not None]
        serialized_values = [_serialize_value(values[key]) for key in columns]
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(serialized_values)})"
        result = self.client.execute(sql)
        return getattr(result, 'last_insert_rowid', None)

    def update(self, table_name: str, ident: int, values: dict):
        assignments = [
            f"{key} = {_serialize_value(value)}"
            for key, value in values.items()
        ]
        if not assignments:
            return
        sql = f"UPDATE {table_name} SET {', '.join(assignments)} WHERE id = {ident}"
        self.client.execute(sql)

    def delete(self, table_name: str, ident: int):
        self.client.execute(f'DELETE FROM {table_name} WHERE id = {ident}')

    def close(self):
        pass


def create_session() -> DatabaseSession:
    return DatabaseSession(_client)


def get_db() -> Generator[DatabaseSession, None, None]:
    session = create_session()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope() -> Generator[DatabaseSession, None, None]:
    session = create_session()
    try:
        yield session
    finally:
        session.close()


get_session = get_db