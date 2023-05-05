from bs4 import BeautifulSoup

# LEN_OF_DESCRIPTION = 190


def get_seo_data(page: object) -> tuple[str]:
    """
    Parse webpage content and return values of
    tags <h1> and <title>, and value of attribute
    content of tag <meta name="description" content="...">.

    :param page: The Response object, which contains
    a server's response to an HTTP request.
    """
    soup = BeautifulSoup(page.text, 'html.parser')
    h1 = soup.h1.get_text() if soup.h1 else ''
    title = soup.title.get_text() if soup.title else ''
    description = ''

    if soup.find('meta', attrs={'name': 'description'}):
        description = soup.find('meta', {'name': 'description'})['content']

        # if len(description) > LEN_OF_DESCRIPTION:
        # description = description[:LEN_OF_DESCRIPTION] + '...'

    return h1, title, description
