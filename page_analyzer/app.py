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
                                VALUES (%s, %s)", (new_url, created_at))
                    flash('Страница добавлена!', 'success')
                except psycopg2.errors.UniqueViolation:
                    flash('Страница уже существует',
                          'warning')
    finally:
        connection.close()

    return redirect(url_for('index'))


def validate(url):
    return validators.url(url, public=True) and len(url) <= 255
