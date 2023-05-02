import pytest
import requests
from page_analyzer.parser import parser


@pytest.mark.parametrize('url, url_data', [
    ("https://peps.python.org",
     ("Python Enhancement Proposals",
      "PEP 0 – Index of Python Enhancement Proposals (PEPs) | peps.python.org",
      "Python Enhancement Proposals (PEPs)")),
    ("https://jinja.palletsprojects.com", (
     "Jinja¶", "Jinja — Jinja Documentation (3.1.x)", ''))
])
def test_parser(url, url_data):
    with requests.get(url) as response:
        result = parser(response)
    assert result == url_data
