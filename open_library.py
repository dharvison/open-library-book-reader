"""Handle OpenLibrary.org API calls"""

import requests

BASE_URL = "https://openlibrary.org"
BOOK_URL = f"{BASE_URL}/api/books"
COVER_ID_URL = "https://covers.openlibrary.org/b/id/"

DEFAULT_SEARCH_FIELDS = "key,isbn,author_name,title,lending_edition_s,ia,availability,cover_i"

#
# Search
#

def do_search(query, fields="*", limit=100, page=1):
    """
    Perform a search for the given query and fields
    
    query is generally based on q=TERM or isbn=ISBN
    fields is * or something like: "key,isbn,author_name,title,lending_edition_s,ia,availability,cover_i"
    limit, page

    returns dict from response json
    """
    
    request_url = f"{ BASE_URL }/search.json?{ query }&fields={ fields }&limit={ limit }&page={ page }"
    print(request_url)

    response = requests.get(request_url)
    resp_data = response.json()

    return resp_data


def keyword_search(keyword, fields=DEFAULT_SEARCH_FIELDS, limit=100, page=1):
    """Search for keyword"""

    query=f"q={ keyword }"
    search_data = do_search(query, fields, limit, page)

    results = {
        'total': search_data.get('numFound', 0),
        'num_returned': 0,
        'works': [],
    }
    for work in search_data.get('docs'):
        work_data = parse_search_data(work)
        if work_data is not None:
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
    if work is not None:
        work_data = parse_search_data(work)
        if work_data is not None:
            return work_data
    
    return None


def parse_search_data(work):
    """parse the search data to a dict"""

    key = work.get('key')
    olid = key.split('/')[-1]
    title = work.get('title')
    author_name = work.get('author_name', [])
    publish_date = work.get('publish_date', [])
    cover_id = work.get('cover_i')
    lending_edition = work.get('lending_edition_s')

    isbn_list = work.get('isbn', [])
    isbn = isbn_list[0] if len(isbn_list) > 0 else None

    availability = work.get('availability')
    if availability is not None:
        # if there is an available ISBN use that instead
        isbn = availability.get('isbn')
        if lending_edition is None:
            lending_edition = availability.get('openlibrary_edition')

    cover_url = f"{COVER_ID_URL}{cover_id}" if cover_id is not None else None
    if lending_edition is not None:
        cover_url = create_cover_url(lending_edition)

    book = {
        'workid': olid,
        'olid': lending_edition if lending_edition is not None else olid,
        'isbn': isbn,
        'title': title,
        'author_name': author_name[0] if len(author_name) > 0 else 'Unknown',
        'cover_url': cover_url,
        'book_url': f"{ BASE_URL }{ key }",
    }

    return book


#
# Fetch data on work and books
#

def fetch_book_data(olid):
    """Fetch data for a book with author data"""

    w_type = work_type(olid)
    fetched_data = fetch_data(olid, w_type)
    book_data = fetched_data.get(f"OLID:{olid}") if w_type == "books" else fetched_data

    if "authors" in book_data:
        author_list = []
        for author in book_data.get("authors"):
            # books and works nest author info differently
            if "name" in author:
                 author_list.append(author.get("name"))
            else:
                to_split = author.get("author") if "author" in author else author
                split_id = to_split["key"].split("/")
                fetched_author = fetch_data(split_id[-1], "authors")
                author_list.append(fetched_author["name"])
        book_data["authors"] = author_list
    
    # books and works handle covers differently
    covers = book_data.get("covers")
    if covers is None and w_type == "books":
        cover_data = fetch_data(olid, "cover")
        covers = cover_data.get("covers")

    if covers is not None and len(covers) > 0:
        book_data["cover_url"] = create_cover_url(olid, w_type)
    else:
        book_data["cover_url"] = None

    return book_data


def fetch_data(olid, data_type):
    """Fetch data for olid and data_type"""

    if data_type == "books":
        request_url = f"{BOOK_URL}?bibkeys=OLID:{olid}&format=json&jscmd=data"
    elif data_type == "cover":
        request_url = f"{BASE_URL}/books/{olid}.json"
    else:
        request_url = f"{BASE_URL}/{data_type}/{olid}.json"
        
    print(request_url)

    response = requests.get(request_url)
    # print(response.status_code)

    data = response.json()
    return data


#
# Availability
#

def fetch_availabilty_links(olid):
    """Fetch availability data and links for olid"""

    w_type = work_type(olid)
    fetched_data = fetch_data(olid, w_type)
    book_data = fetched_data.get(f"OLID:{olid}") if w_type == "books" else fetched_data

    ebook_data = book_data.get("ebooks")[0] if "ebooks" in book_data else None

    availability_links = {
        "ol_url": book_data.get("url"),
        "availability": ebook_data.get("availability") if ebook_data is not None else None,
        "checkedout": ebook_data.get("checkedout") if ebook_data is not None else None,
        "borrow_url": ebook_data.get("borrow_url") if ebook_data is not None else None,
        "read_url": ebook_data.get("read_url") if ebook_data is not None else None,
    }

    return availability_links


#
# Trending books
#

def fetch_trending_books(trending_type, min=4, limit=12):
    """Fetch trending books from the last 24 hours"""

    # default to "recent"
    request_url = f"https://openlibrary.org/trending/hours.json?hours=24&minimum={min}&limit={limit}&sort_by_count=false"
    if trending_type == "new":
        request_url = f"https://openlibrary.org/trending/new.json?minimum={min}&limit={limit}&sort_by_count=false"
    elif trending_type == "popular":
        request_url = f"https://openlibrary.org/trending/popular.json?minimum={min}&limit={limit}&sort_by_count=false"

    response = requests.get(request_url)
    data = response.json()
    works = data.get("works")
    return works

#
# Helper methods
#

def create_cover_url(olid, work_type=None):
    """Generate cover url based on olid and work_type"""

    img_type = "w" if work_type == "works" else "b"
    cover = f"https://covers.openlibrary.org/{img_type}/olid/{olid}"

    return cover


def work_type(olid):
    """Return work type: works, books, author"""

    if olid[-1] == 'W':
        return "works"
    if olid[-1] == 'A':
        return "authors"
    return "books"