import os
from datetime import datetime

import psycopg2
import requests
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from .finder import find_checks, find_url
from .url import normalize_url, validate_url
from .parser import parser

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
    new_url = normalize_url(url_from_request)

    if not validate_url(new_url):
        flash('Некорректный URL', 'alert-danger')
        return redirect(url_for('index'), code=422)

    now = datetime.now()
    created_at = str(now)[:19]  # cutting off microseconds

    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO urls (name, created_at)\
                                   VALUES (%s, %s) RETURNING id",
                                   (new_url, created_at))
                    url_id = cursor.fetchone()[0]  # accessing id from tuple
                    flash('Страница успешно добавлена', 'alert-success')

                except psycopg2.errors.UniqueViolation:
                    url_id, _, created_at = find_url(name=new_url)
                    flash('Страница уже существует', 'alert-warning')
    finally:
        connection.close()

    return render_template('show.html', ID=url_id,
                           name=new_url, created_at=created_at,
                           checks=find_checks(url_id))


@app.route('/urls', methods=['GET'])
def urls() -> str:
    list_of_urls = []
    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM urls ORDER BY id DESC")
                list_of_urls.extend(cursor.fetchall())
    finally:
        connection.close()

    for i, url in enumerate(list_of_urls):
        # accessing info about url's checks by url_id
        checks = find_checks(url[0])
        if checks:
            # adding info about url's last check: time & status code
            list_of_urls[i] = url + (checks[0][6], checks[0][2])
        else:
            continue

    return render_template('list_of_urls.html', urls=list_of_urls)


@app.route('/urls/<int:id>')
def one_url(id: int) -> str:
    url_info = find_url(id=id)

    if url_info is None:
        flash('Такой страницы не существует', 'alert-warning')
        return redirect(url_for('index'))

    _, url_name, url_creating_time = url_info

    return render_template('show.html', ID=id, name=url_name,
                           created_at=url_creating_time,
                           checks=find_checks(id))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id: int) -> str:
    now = datetime.now()
    checked_at = str(now)[:19]  # cutting off microseconds

    _, url_name, _ = find_url(id=id)

    try:
        with requests.get(url_name) as response:
            status_code = response.status_code
            if status_code == 425:
                response.raise_for_status()

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('one_url', id=id), 422)

    url_h1, url_title, description = parser(response)
    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO url_checks (url_id, status_code,\
                               h1, title, description, created_at)\
                               VALUES (%s, %s, %s, %s, %s, %s)",
                               (id, status_code, url_h1,
                                url_title, description, checked_at))
                flash('Страница успешно проверена', 'alert-success')
    finally:
        connection.close()

    return redirect(url_for('one_url', id=id))


@app.errorhandler(psycopg2.OperationalError)
def special_exception_handler(error):
    return render_template('error.html'), 500
