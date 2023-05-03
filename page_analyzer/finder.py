import os
from datetime import datetime

import psycopg2
from psycopg2.extras import NamedTupleCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    return psycopg2.connect(DATABASE_URL)


def find_url(id: int = None, name: str = None) -> tuple[int, str, datetime]:
    """Find a record in the database table 'url' by id or url's name."""
    with connect() as connection:
        with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            if id:
                cursor.execute("SELECT * FROM urls WHERE id = %s",
                               (id, ))
            elif name:
                cursor.execute("SELECT * FROM urls WHERE name = %s",
                               (name, ))
            url_info = cursor.fetchone()

    return url_info


def find_checks(url_id: int) -> list[tuple[int, str, datetime]]:
    """Find a record in the database table 'url_checks' by url's id."""
    url_check_info = []

    with connect() as connection:
        with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute("SELECT * FROM url_checks WHERE url_id = %s\
                           ORDER BY id DESC",
                           (url_id, ))
            url_check_info.extend(cursor.fetchall())

    return url_check_info
