import os
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import requests
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, flash, render_template, request

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def urls_post():
    url_from_request = request.form.to_dict().get('url')
    parsed_url = urlparse(url_from_request)
    new_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

    if not validate(new_url):
        flash('Некорректный URL', 'error')
        return render_template('index.html'), 422

    created_at = datetime.now()

    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO urls (name, created_at)\
                                   VALUES (%s, %s) RETURNING id",
                                   (new_url, created_at))
                    url_id = cursor.fetchone()[0]
                    flash('Страница добавлена!', 'success')

                except psycopg2.errors.UniqueViolation:
                    url_id, new_url, created_at = find_url(url_name=new_url)
                    flash('Страница уже существует', 'warning')
    finally:
        connection.close()

    return render_template('show.html', ID=url_id,
                           name=new_url, created_at=created_at)


def validate(url):
    return validators.url(url, public=True) and len(url) <= 255


@app.route('/urls', methods=['GET'])
def all_urls():
    list_of_urls = []
    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM urls ORDER BY id DESC")
                list_of_urls.extend(cursor.fetchall())
    finally:
        connection.close()

    prepared_list_of_urls = []
    for url in list_of_urls:
        checks = find_checks(url[0])
        if checks:
            url = url + (checks[0][6], )
            url = url + (checks[0][2], )
            prepared_list_of_urls.append(url)
        else:
            prepared_list_of_urls.append(url)

    return render_template('all_urls.html', all_urls=prepared_list_of_urls)


@app.route('/urls/<id>')
def one_url(id):
    url_id, url_name, url_time = find_url(id=id)

    check_info = find_checks(id)

    return render_template('show.html', ID=url_id,
                           name=url_name, created_at=url_time,
                           checks=check_info)


def find_url(id=None, url_name=None):
    url_info = ()
    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                try:
                    if id:
                        cursor.execute("SELECT * FROM urls WHERE id = %s",
                                       (id, ))
                    elif url_name:
                        cursor.execute("SELECT * FROM urls WHERE name = %s",
                                       (url_name, ))
                    url_info = cursor.fetchone()
                except psycopg2.errors.UndefinedTable:
                    url_info = ()
    finally:
        connection.close()
    return url_info


@app.route('/urls/<id>/checks', methods=['POST'])
def check_url(id):
    checked_at = datetime.now()  # date()

    _, url_name, url_time = find_url(id=id)

    try:
        with requests.get(url_name) as r:
            status_code = r.status_code

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'error')
        return render_template('show.html', ID=id,
                               name=url_name, created_at=url_time,
                               checks=find_checks(id)), 422

    soup = BeautifulSoup(r.text, 'html.parser')
    url_h1 = soup.h1.get_text() if soup.h1 else ''
    url_title = soup.title.get_text() if soup.title else ''
    if soup.find('meta', attrs={'name': 'description'}):
        description = soup.find('meta', {'name': 'description'})['content']

    if len(description) > 193:
        description = description[:193] + '...'

    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO url_checks (url_id, status_code,\
                               h1, title, description, created_at)\
                               VALUES (%s, %s, %s, %s, %s, %s)",
                               (id, status_code, url_h1,
                                url_title, description, checked_at))
                flash('Страница успешно проверена', 'success')
    finally:
        connection.close()

    checks = find_checks(id)

    return render_template('show.html', ID=id,
                           name=url_name, created_at=url_time,
                           checks=checks)


def find_checks(url_id):
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
