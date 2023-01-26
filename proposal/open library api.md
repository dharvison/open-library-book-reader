# [OpenLibrary.org](https://openlibrary.org/developers/api)

RESTful APIs for accessing information on books, authors, and more. Here are the main APIs I plan on using.

I'll be using the official [openlibrary-client](https://github.com/internetarchive/openlibrary-client).

## [Search](https://openlibrary.org/dev/docs/api/search)

Search for books and possibly more as needed.

| Parameter | Description |
|-----------|-------------|
| q | Default query param |
| title | Search title |
| author | Search author |
| fields | Specify fields and allows archive.org search via availability. |
| sort | Defaults sort is `relevance` others: new, old, random, key. |

Relevant Data in `docs`
* title
* author_name (List)
* cover_i (for covers API)
* isbn (10 or 13)


## [Books](https://openlibrary.org/dev/docs/api/books)

Retrieve information about specific books. Books API allows for multiple types of IDs. Might use ISBN if that's the primary identifier.

| Parameter | Description |
|-----------|-------------|
| bibkeys=ISBN:`$ISBN` | the ISBN 10 or 13 for the book |

## [Covers](https://openlibrary.org/dev/docs/api/covers)

Book cover image for display.

`https://covers.openlibrary.org/b/isbn/$ISBN-$size.jpg`

* S: small for search results page
* M: medium for detals page

## [Partner/Read](https://openlibrary.org/dev/docs/api/read)

Read or borrow the books

`http://openlibrary.org/api/volumes/brief/isbn/$ISBN.json`

## Other APIs

Here are some other APIs I might use if time permits or as needed.

### [Authors](https://openlibrary.org/dev/docs/api/authors)

Search for author information, and list books by the author.

`https://openlibrary.org/search/authors.json?q=$SEARCH`
`https://openlibrary.org/authors/$ID.json`

### [Search Inside](https://openlibrary.org/dev/docs/api/search_inside)

Find specific text or quotes from books.