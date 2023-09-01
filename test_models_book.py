"""Book model tests."""

# run these tests like:
#
#    python -m unittest test_models_book.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, Book

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///olreader-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():
    db.create_all()


class BookModelTestCase(TestCase):
    """Test model for book"""

    def setUp(self):
        """Create test client, add sample data."""
        
        with app.app_context():
            Book.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up"""

        with app.app_context():
            db.session.rollback()

    def test_book_model(self):
        """Does basic model work?"""
        
        b1 = Book(
            olid = "OL9242915M",
            isbn = "9780061121647",
            title = "Three-Ten to Yuma",
            author = "Elmore Leonard",
            cover_url = "https://covers.openlibrary.org/b/olid/OL9242915M",
        )
        
        with app.app_context():
            db.session.add(b1)
            db.session.commit()

            # Book data should match
            self.assertEqual(b1.olid, "OL9242915M")
            self.assertEqual(b1.isbn, "9780061121647")
            self.assertEqual(b1.title, "Three-Ten to Yuma")
            self.assertEqual(b1.author, "Elmore Leonard")

    def test_repr_book(self):
        """Does book __repr__ work?"""

        b1 = Book(
            olid = "OL35268128M",
            title = "Adventures of Sherlock Holmes",
            author = "Arthur Conan Doyle",
            cover_url = "https://covers.openlibrary.org/b/olid/OL35268128M",
        )

        with app.app_context():
            db.session.add(b1)
            db.session.commit()

            expected = f"<Book {b1.olid}: {b1.title}, {b1.author}>"
            self.assertEqual(b1.__repr__(), expected)
    
    def test_display_book(self):
        """Does helper method display_book output correct data?"""

        b1 = Book(
            olid = "99999",
            title = "Sample Book for Display",
            author = "PKD",
        )

        with app.app_context():
            db.session.add(b1)
            db.session.commit()

            expected = f"{b1.title} by {b1.author}"
            self.assertEqual(b1.display_book(), expected)

    def test_to_dict(self):
        """Values returned by to_dict method should match DB"""

        book_dict = {
            "olid": "OL26992991M",
            "isbn": "9781619634466",
            "title": "A Court of Mist and Fury",
            "author": "Sarah J. Maas",
            "cover_url": "https://covers.openlibrary.org/b/olid/OL26992991M",
        }

        b1 = Book(
            olid = book_dict.get("olid"),
            isbn = book_dict.get("isbn"),
            title = book_dict.get("title"),
            author = book_dict.get("author"),
            cover_url = book_dict.get("cover_url"),
        )

        with app.app_context():
            db.session.add(b1)
            db.session.commit()

            # Book data should match
            self.assertDictEqual(b1.to_dict(), book_dict)
    
    def test_create_book(self):
        """test creation of book from olid and isbn"""
        # TODO requires mock

        raise(Exception('implement me!'))
