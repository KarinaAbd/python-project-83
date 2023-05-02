from bs4 import BeautifulSoup


LEN_OF_DESCRIPTION = 190


def parser(page: object) -> tuple[str]:
    """
    Parse webpage content and return values of
    tags <h1> and <title>, and value of attribute
    content of tag <meta name="description" content="...">.

    :param page: The Response object, which contains
    a server's response to an HTTP request.
    """
    soup = BeautifulSoup(page.text, 'html.parser')
    url_h1 = soup.h1.get_text() if soup.h1 else ''
    url_title = soup.title.get_text() if soup.title else ''
    description = ''

    if soup.find('meta', attrs={'name': 'description'}):
        description = soup.find('meta', {'name': 'description'})['content']

        if len(description) > LEN_OF_DESCRIPTION:
            description = description[:LEN_OF_DESCRIPTION] + '...'

    return url_h1, url_title, description
