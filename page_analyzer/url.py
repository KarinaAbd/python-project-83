from urllib.parse import urlparse

import validators

MAX_URL_LEN = 255


def normalize_url(url: str) -> str:
    """Truncates the URL to the <protocol>://<domain name> structure"""
    parsed_url = urlparse(url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}'


def validate_url(url: str) -> bool:
    """Validate url by rules (https://gist.github.com/dperini/729294)."""
    if url == '':
        return 0
    return 1 if validators.url(url) and len(url) <= MAX_URL_LEN else -1
