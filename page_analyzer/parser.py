from bs4 import BeautifulSoup


LEN_OF_DESCRIPTION = 190


def parser(page):
    soup = BeautifulSoup(page.text, 'html.parser')
    url_h1 = soup.h1.get_text() if soup.h1 else ''
    url_title = soup.title.get_text() if soup.title else ''
    description = ''

    if soup.find('meta', attrs={'name': 'description'}):
        description = soup.find('meta', {'name': 'description'})['content']
        if len(description) > LEN_OF_DESCRIPTION:
            description = description[:LEN_OF_DESCRIPTION] + '...'

    return url_h1, url_title, description
