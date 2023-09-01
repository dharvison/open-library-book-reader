"""BookList model tests."""

# run these tests like:
#
#    python -m unittest test_models_booklist.py


import os
from unittest import TestCase
from unittest.mock import patch
from sqlalchemy import exc

from models import db, User, Book, BookList

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


class BookListModelTestCase(TestCase):
    """Test model for booklist"""

    def setUp(self):
        """Create test client, add sample data."""
        
        with app.app_context():
            Book.query.delete()
            BookList.query.delete()
            User.query.delete()

            # dummy books
            b1 = Book(
                olid = "12345",
                title = "Watchmen",
                author = "Alan Moore",
                cover_url = "https://covers.openlibrary.org/b/id/6459694",
            )

            b2 = Book(
                olid = "11111",
                title = "Catch-22",
                author = "Joseph Heller",
                cover_url = "https://covers.openlibrary.org/b/id/13061725",
            )

            u1 = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD",
                bio="test",
                is_admin=False
            )

            db.session.add_all([b1, b2, u1])
            db.session.commit()
            self.user_id=u1.id
            self.test_book1=b1
            self.test_book2=b2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up"""

        with app.app_context():
            db.session.rollback()

    def test_booklist_model(self):
        """Does basic model work?"""
        
        l1 = BookList(
            user_id=self.user_id,
            title="test list",
            blurb="test blurb"
        )
        
        with app.app_context():
            db.session.add(l1)
            db.session.commit()

            # List should have no books & the correct user
            self.assertEqual(len(l1.books), 0)
            self.assertEqual(l1.user.id, self.user_id)
    
    def test_booklist_edit(self):
        """Edits to title and blurb should be reflected"""
        
        init_title="test list"
        init_blurb="test blurb"
        l1 = BookList(
            user_id=self.user_id,
            title=init_title,
            blurb=init_blurb
        )
        
        with app.app_context():
            db.session.add(l1)
            db.session.commit()

            self.assertEqual(l1.title, init_title)
            self.assertEqual(l1.blurb, init_blurb)

            update_title="new title"
            update_blurb="new blurb"
            l1.title=update_title
            l1.blurb=update_blurb

            db.session.add(l1)
            db.session.commit()

            self.assertEqual(l1.title, update_title)
            self.assertEqual(l1.blurb, update_blurb)

    def test_add_book(self):
        """Is books link working?"""

        l1 = BookList(
            user_id=self.user_id,
            title="test list",
            blurb="test blurb"
        )
        
        with app.app_context():
            db.session.add(l1)
            db.session.commit()

            self.assertEqual(l1.user.id, self.user_id)
            self.assertEqual(len(l1.books), 0)

            # add test book
            l1.books.append(self.test_book1)
            self.assertEqual(len(l1.books), 1)
            # another
            l1.books.append(self.test_book2)
            self.assertEqual(len(l1.books), 2)

    def test_add_olid_existing(self):
        """Test that adding an existing book by olid works"""

        l1 = BookList(
            user_id=self.user_id,
            title="test list",
            blurb="test blurb"
        )
        
        with app.app_context():
            db.session.add(l1)
            db.session.commit()

            self.assertEqual(l1.user.id, self.user_id)
            self.assertEqual(len(l1.books), 0)

            # add test book
            l1.add_olid("12345")
            self.assertEqual(len(l1.books), 1)

    def test_add_olid_create(self):
        """Test that adding book olid works with creation"""

        l1 = BookList(
            user_id=self.user_id,
            title="test list",
            blurb="test blurb"
        )
        
        with app.app_context():
            db.session.add(l1)
            db.session.commit()

            self.assertEqual(l1.user.id, self.user_id)
            self.assertEqual(len(l1.books), 0)

            # add test book
            with patch("models.Book.create_book") as mock_create:
                mock_create.return_value = self.test_book2
                l1.add_olid("AAAAAAAAA")
                mock_create.assert_called_once()
                self.assertEqual(len(l1.books), 1)
