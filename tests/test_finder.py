import os

import pytest
from dotenv import load_dotenv

from page_analyzer.finder import find_checks, find_url

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@pytest.mark.parametrize('id, url', [
    (1, 'https://postgrespro.ru'),
    (2, 'https://github.com')
])
def test_find_url(id, url):
    result_1 = find_url(id=id)
    assert result_1[1] == url

    result_2 = find_url(name=url)
    assert result_2[0] == id


@pytest.mark.parametrize('url_id, check_id, status_code, h1', [
    (33, 70, 200, ''),
    (15, 46, 200, 'Python Enhancement Proposals')
])
def test_find_checks(url_id, check_id, status_code, h1):
    result_1 = find_checks(url_id)
    assert result_1[-1][0] == check_id
    assert result_1[-1][2] == status_code
    assert result_1[-1][3] == h1
