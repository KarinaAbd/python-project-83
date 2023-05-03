import os
from datetime import datetime

import psycopg2
from psycopg2.extras import NamedTupleCursor
import requests
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from .finder import connect, find_checks, find_url
from .parser import parser
from .url import normalize_url, validate_url

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET


@app.route('/')
def index() -> str:
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def urls_post() -> str:
    url_from_request = request.form.to_dict().get('url')

    if not validate_url(url_from_request):
        flash('Некорректный URL', 'alert-danger')
        return render_template('index.html'), 422

    new_url = normalize_url(url_from_request)
    now = datetime.now()
    created_at = str(now)[:19]  # cutting off microseconds

    with connect() as connection:
        with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            try:
                cursor.execute("INSERT INTO urls (name, created_at)\
                                VALUES (%s, %s) RETURNING id",
                               (new_url, created_at))
                url_info = cursor.fetchone()
                url_id = url_info.id  # accessing id from named tuple
                flash('Страница успешно добавлена', 'alert-success')

            except psycopg2.errors.UniqueViolation:
                url = find_url(name=new_url)
                url_id = url.id
                flash('Страница уже существует', 'alert-warning')

    return redirect(url_for('one_url', id=url_id))


@app.route('/urls', methods=['GET'])
def urls() -> str:
    urls = []

    with connect() as connection:
        with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute("SELECT * FROM urls ORDER BY id DESC")
            urls.extend(cursor.fetchall())

    for i, url in enumerate(urls):
        # accessing info about url's checks by url_id
        checks = find_checks(url.id)
        if checks:
            # adding info about url's last check
            urls[i] = url + (checks[0].created_at, checks[0].status_code)
        else:
            continue

    return render_template('list_of_urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=['GET'])
def one_url(id: int) -> str:
    url = find_url(id=id)

    if url is None:
        flash('Такой страницы не существует', 'alert-warning')
        return redirect(url_for('index'))

    return render_template('show.html', ID=id, name=url.name,
                           created_at=url.created_at,
                           checks=find_checks(id))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id: int) -> str:
    now = datetime.now()
    checked_at = str(now)[:19]  # cutting off microseconds

    url = find_url(id=id)

    try:
        with requests.get(url.name) as response:
            status_code = response.status_code
            if status_code != 200:
                response.raise_for_status()

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return render_template('show.html', ID=id, name=url.name,
                               created_at=url.created_at,
                               checks=find_checks(id)), 422

    h1, title, description = parser(response)

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO url_checks (url_id, status_code,\
                           h1, title, description, created_at)\
                           VALUES (%s, %s, %s, %s, %s, %s)",
                           (id, status_code, h1,
                            title, description, checked_at))
            flash('Страница успешно проверена', 'alert-success')

    return redirect(url_for('one_url', id=id))


@app.errorhandler(psycopg2.OperationalError)
def special_exception_handler(error) -> str:
    return render_template('error.html'), 500
