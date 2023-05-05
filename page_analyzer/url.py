from urllib.parse import urlparse

import validators
from flask import flash

MAX_URL_LEN = 255


def normalize_url(url: str) -> str:
    """Truncates the URL to the <protocol>://<domain name> structure"""
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def validate_url(url: str) -> bool:
    """Validate url by rules (https://gist.github.com/dperini/729294)."""
    if url == '':
        flash('URL обязателен', 'alert-danger')
    return validators.url(url) and len(url) <= MAX_URL_LEN
