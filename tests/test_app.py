import pytest

from page_analyzer import app
from flask import request
import responses
import requests


@pytest.fixture()
def test_app():
    test_app = app()
    test_app.config.update({"TESTING": True})
    # other setup can go here
    yield test_app
    # clean up / reset resources here


@pytest.fixture()
def client(test_app):
    return test_app.test_client()


def test_index():
    with app.test_request_context('/', method='GET'):
        assert request.path == '/'
        assert request.method == 'GET'


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

# как это переписать под моё приложение? получается опять нужно
# на реальный сервер отправлять запрос


def test_api(mocked_responses):
    mocked_responses.get(
        "https://github.com",
        body="{}",
        status=200,
        content_type="application/json",
    )
    resp = requests.get("https://github.com")
    assert resp.status_code == 200
