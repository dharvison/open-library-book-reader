"""OpenLibrary API tests."""

# run these tests like:
#
#    python -m unittest test_models_book.py


from unittest import TestCase
from unittest.mock import patch

from open_library import fetch_book_data, work_type, create_cover_url, parse_search_data


class OpenLibraryAPITestCase(TestCase):
    """Test open library API"""

    def setUp(self):
        """Create test client, add sample data."""
        
        # self.client = app.test_client()
        self.mock_data = {"OLID:OL26992991M": {"url": "https://openlibrary.org/books/OL26992991M/A_Court_of_Mist_and_Fury", "key": "/books/OL26992991M", "title": "A Court of Mist and Fury", "authors": [{"url": "https://openlibrary.org/authors/OL7115219A/Sarah_J._Maas", "name": "Sarah J. Maas"}], "number_of_pages": 640, "identifiers": {"isbn_10": ["1619634465"], "isbn_13": ["9781619634466"], "openlibrary": ["OL26992991M"]}, "classifications": {"lc_classifications": ["PZ7.M111575Com 2016"]}, "publishers": [{"name": "Bloomsbury"}], "publish_date": "2016-05", "subjects": [{"name": "Fantasy", "url": "https://openlibrary.org/subjects/fantasy"}, {"name": "Fiction", "url": "https://openlibrary.org/subjects/fiction"}, {"name": "Fairies", "url": "https://openlibrary.org/subjects/fairies"}, {"name": "Blessing and cursing", "url": "https://openlibrary.org/subjects/blessing_and_cursing"}, {"name": "Fantasy fiction", "url": "https://openlibrary.org/subjects/fantasy_fiction"}, {"name": "Fairies, fiction", "url": "https://openlibrary.org/subjects/fairies,_fiction"}, {"name": "nyt:young-adult-hardcover=2016-05-22", "url": "https://openlibrary.org/subjects/nyt:young-adult-hardcover=2016-05-22"}, {"name": "New York Times bestseller", "url": "https://openlibrary.org/subjects/new_york_times_bestseller"}, {"name": "nyt:young-adult-e-book=2016-05-22", "url": "https://openlibrary.org/subjects/nyt:young-adult-e-book=2016-05-22"}, {"name": "collectionID:TexChallenge2021", "url": "https://openlibrary.org/subjects/collectionid:texchallenge2021"}, {"name": "collectionID:KellerChallenge", "url": "https://openlibrary.org/subjects/collectionid:kellerchallenge"}, {"name": "collectionID:EanesChallenge", "url": "https://openlibrary.org/subjects/collectionid:eaneschallenge"}, {"name": "collectionID:AlpineChallenge", "url": "https://openlibrary.org/subjects/collectionid:alpinechallenge"}, {"name": "Adaptations", "url": "https://openlibrary.org/subjects/adaptations"}, {"name": "Magic", "url": "https://openlibrary.org/subjects/magic"}, {"name": "Courts and courtiers", "url": "https://openlibrary.org/subjects/courts_and_courtiers"}, {"name": "F\u00e9es", "url": "https://openlibrary.org/subjects/f\u00e9es"}, {"name": "Romans, nouvelles, etc. pour la jeunesse", "url": "https://openlibrary.org/subjects/romans,_nouvelles,_etc._pour_la_jeunesse"}, {"name": "Cours et courtisans", "url": "https://openlibrary.org/subjects/cours_et_courtisans"}, {"name": "Fantasy & Magic", "url": "https://openlibrary.org/subjects/fantasy_&_magic"}, {"name": "Love & Romance", "url": "https://openlibrary.org/subjects/love_&_romance"}, {"name": "Action & Adventure", "url": "https://openlibrary.org/subjects/action_&_adventure"}, {"name": "General", "url": "https://openlibrary.org/subjects/general"}, {"name": "series:A_Court_of_Thorns_and_Roses", "url": "https://openlibrary.org/subjects/series:a_court_of_thorns_and_roses"}], "subject_people": [{"name": "Tam Lin (Legendary character)", "url": "https://openlibrary.org/subjects/person:tam_lin_(legendary_character)"}], "ebooks": [{"preview_url": "https://archive.org/details/courtofmistfury0000maas", "availability": "restricted", "formats": {}}], "covers": {"small": "https://covers.openlibrary.org/b/id/14315081-S.jpg", "medium": "https://covers.openlibrary.org/b/id/14315081-M.jpg", "large": "https://covers.openlibrary.org/b/id/14315081-L.jpg"}}}
        self.search_data  = {"numFound": 327, "start": 0, "numFoundExact": True,  "docs":[
                {
                    "key": "/works/OL2897798W",
                    "title": "Watchmen",
                    "isbn": [
                        "9781401248192",
                        "1631400304",
                        "9781401219260",
                        "9781779500922",
                        "8416998728",
                        "9788416998722",
                        "1779501129",
                        "9788573515497",
                        "9781852860240",
                        "2809406405",
                        "9781401265564",
                        "9781631400308",
                        "1401219268",
                        "0613919645",
                        "9780446386890",
                        "1779500920",
                        "9782809406405",
                        "1401207138",
                        "9781401238964",
                        "9788467473278",
                        "9780606357425",
                        "1401245250",
                        "857351549X",
                        "1401238963",
                        "9783866076075",
                        "386607607X",
                        "9781401207137",
                        "9780613919647",
                        "140128471X",
                        "9780930289232",
                        "1401248195",
                        "1852860243",
                        "0930289234",
                        "8467473274",
                        "0446386898",
                        "1401265561",
                        "0606357424",
                        "9781779501127",
                        "9781401245252",
                        "9781401284718"
                    ],
                    "ia": [
                        "watchmen0000moor_e6p3",
                        "watchmen00moor_0",
                        "watchmen00moor",
                        "watchmen0000moor",
                        "watchmen00moor_0"
                    ],
                    "lending_edition_s": "OL15479330M",
                    "cover_i": 7774899,
                    "author_name": [
                        "Alan Moore",
                        "Dave Gibbons",
                        "John Higgins"
                    ],
                    "availability": {
                        "status": "borrow_available",
                        "available_to_browse": True,
                        "available_to_borrow": True,
                        "available_to_waitlist": False,
                        "is_printdisabled": True,
                        "is_readable": False,
                        "is_lendable": True,
                        "is_previewable": True,
                        "identifier": "watchmen0000moor_e6p3",
                        "isbn": "9780930289232",
                        "oclc": None,
                        "openlibrary_work": "OL2897798W",
                        "openlibrary_edition": "OL15479330M",
                        "last_loan_date": None,
                        "num_waitlist": None,
                        "last_waitlist_date": None,
                        "is_restricted": True,
                        "is_browseable": True,
                        "__src__": "core.models.lending.get_availability"
                    }
                }
            ],
            "num_found": 327,
            "q": "watchmen",
            "offset": None
        }

    def tearDown(self):
        """Clean up"""

        # with app.app_context():
        #     db.session.rollback()

    #
    # Helper methods
    #

    def test_work_type(self):
        """Type check works"""

        self.assertEqual(work_type('OL9242915W'), 'works')
        self.assertEqual(work_type('OL35268128A'), 'authors')
        self.assertEqual(work_type('OL26992991M'), 'books')

    def test_create_cover_url(self):
        """Cover urls should match type and format"""

        self.assertEqual(create_cover_url('OL9242915W', 'works'), "https://covers.openlibrary.org/w/olid/OL9242915W")
        self.assertEqual(create_cover_url('OL26992991M', 'books'), "https://covers.openlibrary.org/b/olid/OL26992991M")
        self.assertEqual(create_cover_url('OL26992991M'), "https://covers.openlibrary.org/b/olid/OL26992991M")

    #
    # Search and Parse data
    #

    def test_parse_search_data(self):
        """test parsing search data"""

        data = parse_search_data(self.search_data['docs'][0])
        
        self.assertEqual(data["olid"], "OL15479330M")
        self.assertEqual(data["title"], "Watchmen")
        self.assertEqual(data["author_name"], "Alan Moore")

    def test_fetch_book_data(self):
        """test fetch book from olid w/ mock data"""

        with patch("open_library.fetch_data") as mock_fetch:
            mock_fetch.return_value = self.mock_data
            new_book = fetch_book_data("OL26992991M")
            mock_fetch.assert_called_once()
            
            self.assertEqual(new_book["title"], "A Court of Mist and Fury")
            self.assertEqual(new_book["authors"], ["Sarah J. Maas"])
