import os
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

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
        return redirect(url_for('index'))

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

    return render_template('all_urls.html', all_urls=list_of_urls)


@app.route('/urls/<id>')
def one_url(id):
    url_id, url_name, url_time = find_url(id=id)
    return render_template('show.html', ID=url_id,
                           name=url_name, created_at=url_time)


@app.route('/urls/<id>/checks', methods=['POST'])
def check_url(id):
    pass


def find_url(id=None, url_name=None):
    url_info = ()
    connection = psycopg2.connect(DATABASE_URL)
    try:
        with connection:
            with connection.cursor() as cursor:
                if id:
                    cursor.execute("SELECT * FROM urls WHERE id = %s", (id, ))
                elif url_name:
                    cursor.execute("SELECT * FROM urls WHERE name = %s",
                                   (url_name, ))
                url_info = cursor.fetchone()
    finally:
        connection.close()
    return url_info
