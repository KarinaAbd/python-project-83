def get_seo_data(html: object) -> tuple[str]:
    """
    Parse html content and return values of
    tags <h1> and <title>, and value of attribute
    content of tag <meta name="description" content="...">.

    :param html: The BeautifulSoup object, which represents
    the document as a nested data structure.
    """
    h1 = html.h1.get_text() if html.h1 else ''
    title = html.title.get_text() if html.title else ''

    description = html.find('meta', {'name': 'description'})
    description_content = description['content'] if description else ''

    return h1, title, description_content
