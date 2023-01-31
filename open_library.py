"""Handle OpenLibrary.org API calls"""

import requests

BASE_URL = "https://openlibrary.org/"
COVER_URL = "https://covers.openlibrary.org/b/olid/"
COVER_M_POSTFIX = "-M.jpg"
COVER_S_POSTFIX = "-S.jpg"
BOOK_URL = f"{BASE_URL}books/"

def qd_search(term):
    """quick and dirty search as poc"""

    concat_search = term.replace(" ", "+")
    url = f"{ BASE_URL }search.json?q={ concat_search }"
    print(url)

    response = requests.get(url)
    print(response.status_code)
    data = response.json()
    # for k in data['docs'][0].keys():
    #     print(k)

    results = {
        'total': data.get('numFound', 0),
        'num_returned': len(data.get('docs')),
        'works': [],
    }
    for work in data.get('docs'):
        results.get('works').append(parse_data(work))

    return results

def parse_data(work):
    """parse the work to a dict/Object when it's done"""

    key = work.get('key')
    title = work.get('title')
    author_key = work.get('author_key', [])
    author_name = work.get('author_name', [])
    publish_date = work.get('publish_date', [])
    cover_edition_key = work.get('cover_edition_key')
    lending_edition_s = work.get('lending_edition_s')
    book_url = f"{ BOOK_URL }{ lending_edition_s }" if lending_edition_s != None and len(lending_edition_s) > 0 else ""

    book = {
        'key': key,
        'title': title,
        'author_name': author_name[0] if len(author_name) > 0 else None,
        'author_key': author_key[0] if len(author_key) > 0 else None,
        'publish_date': publish_date[0] if len(publish_date) > 0 else None,
        'cover_url': f"{COVER_URL}{cover_edition_key}{COVER_S_POSTFIX}" if cover_edition_key != None else None,
        'lending_edition_s': lending_edition_s,
        'book_url': book_url,
    }

    return book