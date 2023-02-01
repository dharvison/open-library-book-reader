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

    results = { # TODO Remove total and num
        'total': data.get('numFound', 0),
        'num_returned': 0, #len(data.get('docs')),
        'works': [],
    }
    for work in data.get('docs'):
        work_data = parse_data(work)
        if work_data != None:
            results.get('works').append(work_data)
            results['num_returned'] = results.get('num_returned') + 1

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

    if key != None:
        book = {
            'key': key,
            'title': title,
            'author_name': author_name[0] if len(author_name) > 0 else 'Unknown',
            'author_key': author_key[0] if len(author_key) > 0 else None,
            'publish_date': publish_date[0] if len(publish_date) > 0 else None,
            'cover_url': f"{COVER_URL}{cover_edition_key}{COVER_S_POSTFIX}" if cover_edition_key != None else None,
            'lending_edition_s': lending_edition_s,
            'book_url': f"{ BOOK_URL }{ lending_edition_s }" if lending_edition_s != None and len(lending_edition_s) > 0 else "",
        }
    else:
        book = None

    return book

def fetch_book_data(olid, work_type):
    """Fetch data for a book with author data"""

    book_data = fetch_work_data(olid, work_type)

    authors = book_data['authors']
    author_list = []
    for author in authors:
        split_id = author["author"]["key"].split("/")
        fetched_author = fetch_work_data(split_id[-1], "authors")
        author_list.append(fetched_author["name"])
    book_data["authors"] = author_list
    
    book_data["cover_url"] = create_cover_url(olid, work_type)

    return book_data


def fetch_work_data(olid, work_type):
    """Fetch data for olid and work_type"""

    request_url = f"{BASE_URL}{work_type}/{olid}.json"
    print(request_url)

    response = requests.get(request_url)
    print(response.status_code)

    data = response.json()
    return data


def create_cover_url(olid, work_type):
    """Generate cover url based on olid and work_type"""

    img_type = "w" if work_type == "works" else "b"
    cover = f"https://covers.openlibrary.org/{img_type}/olid/{olid}{COVER_M_POSTFIX}" # Possibly just the stem
    print(cover)

    return cover