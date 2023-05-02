import pytest

from page_analyzer.url import normalize_url, validate_url
import validators


@pytest.mark.parametrize('url, expected', [
    ('https://github.com/KarinaAbd/python-project-83', 'https://github.com'),
    ('https://ru.hexlet.io/projects/83/members/30669', 'https://ru.hexlet.io')
])
def test_normalize_url(url, expected):
    assert expected == normalize_url(url)


@pytest.mark.parametrize('url, expected', [
    ('https://github.com', True),
    ('https://www.youtube.com', True)
])
def test_validate_url(url, expected):
    assert expected == validate_url(url)


@pytest.mark.parametrize('url', ['http://127.0.0.1:5000', 'www.youtube.ru'])
def test_exception_in_validate_url(url):
    validate_url(url)
    assert validators.ValidationFailure
