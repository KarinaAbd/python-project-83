from urllib.parse import urlparse

import validators

MAX_URL_LEN = 255


def normalize_url(url: str) -> str:
    """Truncates the URL to the <protocol>://<domain name> structure"""
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def validate_url(url: str) -> list[str]:
    """Validate url by rules (https://gist.github.com/dperini/729294)."""
    errors = []
    if url == '':
        errors.append('No url')

    if errors or not validators.url(url) or len(url) > MAX_URL_LEN:
        errors.append('Not valid url')

    return errors
