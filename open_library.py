"""Handle OpenLibrary.org API calls"""

import requests

BASE_URL = "https://openlibrary.org/"
BOOK_URL = f"{BASE_URL}books/"

COVER_URL = "https://covers.openlibrary.org/b/olid/"
COVER_S_POSTFIX = "-S.jpg"
COVER_M_POSTFIX = "-M.jpg"
COVER_L_POSTFIX = "-L.jpg"

DEFAULT_SEARCH_FIELDS = "key,isbn,author_name,title,lending_edition_s,ia,availability,cover_edition_key,publish_date"

def qd_search(term):
    """quick and dirty search as poc"""
    print("****************** DON'T USE THIS SEARCH use do_search instead! ******************")
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

def do_search(query, fields="*", limit=100, offset=0):
    """
    Perform a search for the given query and fields
    
    query is generally based on q=TERM or isbn=ISBN
    fields is * or something like: "key,isbn,author_name,title,lending_edition_s,ia,availability,cover_edition_key"
    limit, offset

    returns dict from response json
    """
    
    request_url = f"{ BASE_URL }search.json?{ query }&fields={ fields }&limit={ limit }&offset={ offset }"
    print(request_url)

    response = requests.get(request_url)
    print(response.status_code)
    resp_data = response.json()

    return resp_data


def keyword_search(keyword, fields=DEFAULT_SEARCH_FIELDS, limit=100, offset=0):
    """Search for keyword"""

    query=f"q={ keyword }"
    search_data = do_search(query, fields, limit, offset)

    results = {
        'total': search_data.get('numFound', 0),
        'num_returned': 0, #len(data.get('docs')),
        'works': [],
    }
    for work in search_data.get('docs'):
        work_data = parse_data(work)
        if work_data != None:
            results.get('works').append(work_data)
            results['num_returned'] = results.get('num_returned') + 1

    return results


def isbn_search(isbn, fields=DEFAULT_SEARCH_FIELDS):
    """Search for books with ISBN10 or ISBN13"""

    query = f"isbn={ isbn }"
    isbn_data = do_search(query, fields, limit=1) # should only have 1 result!

    if (isbn_data.get(numFound, 0) > 1):
        print(f"WARNING: Search for { isbn } yielded more than 1 result")

    work = isbn_data.get("docs", None)
    if work != None:
        work_data = parse_data(work)
        if work_data != None:
            return work_data
    
    return None


def parse_data(work): # TODO need to update for all the fields? or maybe I can drop this?
    """parse the work to a dict/Object when it's done"""

    key = work.get('key')
    isbn = work.get('isbn', [])
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
            'isbn': isbn[0] if len(isbn) > 0 else None,
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

# https://openlibrary.org/api/books?bibkeys=ISBN:1779501129,ISBN:9781784083014,OLID:OL1543504M&format=json&jscmd=data
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
    cover = f"https://covers.openlibrary.org/{img_type}/olid/{olid}" # Possibly just the stem

    return cover