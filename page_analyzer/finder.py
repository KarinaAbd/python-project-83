import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def find_url(id: int = None, name: str = None) -> tuple[int, str, datetime]:
    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                if id:
                    cursor.execute("SELECT * FROM urls WHERE id = %s",
                                   (id, ))
                elif name:
                    cursor.execute("SELECT * FROM urls WHERE name = %s",
                                   (name, ))
                url_info = cursor.fetchone()
    finally:
        connection.close()

    return url_info


def find_checks(url_id: int) -> list[tuple[int, str, datetime]]:
    url_check_info = []
    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM url_checks WHERE url_id = %s\
                               ORDER BY id DESC",
                               (url_id, ))
                url_check_info.extend(cursor.fetchall())
    finally:
        connection.close()
    return url_check_info
