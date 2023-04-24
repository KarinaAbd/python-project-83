import pytest

from page_analyzer import app
from flask import request


@pytest.fixture()
def test_app():
    test_app = app()
    app.config.update({"TESTING": True})
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
