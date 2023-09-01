"""BookNote model tests."""

# run these tests like:
#
#    python -m unittest test_models_booknote.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Book, BookNote

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


class BookNoteModelTestCase(TestCase):
    """Test model for booknote"""

    def setUp(self):
        """Create test client, add sample data."""
        
        with app.app_context():
            Book.query.delete()
            BookNote.query.delete()
            User.query.delete()

            # dummy books
            b1 = Book(
                olid = "12345",
                title = "Watchmen",
                author = "Alan Moore",
                cover_url = "https://covers.openlibrary.org/b/id/6459694",
            )

            u1 = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD",
                bio="test",
                is_admin=False
            )

            db.session.add_all([b1, u1])
            db.session.commit()
            self.user_id=u1.id
            self.book_id=b1.olid

        self.client = app.test_client()

    def tearDown(self):
        """Clean up"""

        with app.app_context():
            db.session.rollback()

    def test_booknote_model(self):
        """Does basic model work?"""
        
        n1 = BookNote(
            user_id=self.user_id,
            book_olid=self.book_id,
            note="test note",
            read=False
        )
        
        with app.app_context():
            db.session.add(n1)
            db.session.commit()

            # Note should have correct book & user
            self.assertEqual(n1.user_id, self.user_id)
            self.assertEqual(n1.book_olid, self.book_id)
    
    def test_booknote_edit(self):
        """Edits to note and read should be reflected"""
        
        init_note="test note"
        init_read=False
        n1 = BookNote(
            user_id=self.user_id,
            book_olid=self.book_id,
            note=init_note,
            read=init_read
        )
        
        with app.app_context():
            db.session.add(n1)
            db.session.commit()

            # Note should have correct book & user
            self.assertEqual(n1.user_id, self.user_id)
            self.assertEqual(n1.book_olid, self.book_id)
            self.assertEqual(n1.note, init_note)
            self.assertEqual(n1.read, init_read)

            update_note="new note!"
            n1.note=update_note
            n1.read=not init_read

            db.session.add(n1)
            db.session.commit()

            self.assertEqual(n1.note, update_note)
            self.assertNotEqual(n1.read, init_read)
