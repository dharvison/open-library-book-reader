"""User model tests."""

# run these tests like:
#
#    python -m unittest test_models_user.py


import os
from unittest import TestCase
from sqlalchemy import exc
from flask_bcrypt import Bcrypt

from models import db, User, Book, BookNote, BookList

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///olreader-test"

# Now we can import app
from app import app

bcrypt = Bcrypt()
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():
    db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users"""

    def setUp(self):
        """Create test client, add sample data."""
        
        with app.app_context():
            Book.query.delete()
            BookNote.query.delete()
            BookList.query.delete()
            User.query.delete()

            # dummy book
            b1 = Book(
                olid = "12345",
                title = "Watchmen",
                author = "Alan Moore",
                cover_url = "https://covers.openlibrary.org/b/id/6459694",
            )

            db.session.add_all([b1])
            db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up"""

        with app.app_context():
            db.session.rollback()

    @classmethod
    def create_test_user(cls, username):
        """Create test User from username"""

        return User(
            email=f"{username}@test.com",
            username=username,
            password="HASHED_PASSWORD",
            bio=f"{username} bio",
            is_admin=False
        )

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            bio="test",
            is_admin=False
        )

        with app.app_context():
            db.session.add(u)
            db.session.commit()

            # User should have no notes & no lists
            self.assertEqual(len(u.notes), 0)
            self.assertEqual(len(u.lists), 0)
    
    def test_repr_user(self):
        """Does user __repr__ work?"""

        u = UserModelTestCase.create_test_user("test_user1")
        with app.app_context():
            db.session.add(u)
            db.session.commit()

            expected = f"<User #{u.id}: {u.username}, {u.email}>"
            self.assertEqual(u.__repr__(), expected)
    
    def test_user_list(self):
        """Are lists correctly connected to user?"""

        u1 = UserModelTestCase.create_test_user("list_test")
        with app.app_context():
            db.session.add(u1)
            db.session.commit()
            l1 = BookList(
                user_id=u1.id,
                title="test list",
                blurb="test blurb"
            )
            u1.lists.append(l1)
            db.session.commit()

            self.assertEqual(len(u1.lists), 1)
    
    def test_user_note(self):
        """Are notes correctly connected to user?"""

        u1 = UserModelTestCase.create_test_user("note_test")
        with app.app_context():
            db.session.add(u1)
            db.session.commit()
            n1 = BookNote(
                user_id=u1.id,
                book_olid="12345",
                read=False,
                note="test blurb"
            )
            u1.notes.append(n1)
            db.session.commit()

            self.assertEqual(len(u1.notes), 1)
    
    def test_user_signup(self):
        """Does user signup work?"""

        # hashed = bcrypt.hashpw(password, bcrypt.gensalt(14))
        username = "signup_test"
        email = "signup@test.com"
        password = "welcome1"
        with app.app_context():
            u1 = User.signup(username, email, password)
            self.assertEqual(u1.username, username)
            self.assertEqual(u1.email, email)
            self.assertEqual(bcrypt.check_password_hash(u1.password, password), True)

    def test_user_authenticate(self):
        """Authenticate should detect correct password"""

        username="testuser"
        password="welcome1"
        u1 = User(
            username=username,
            password=bcrypt.generate_password_hash(password).decode('UTF-8'),
            email="test@test.com",
            bio="test",
            is_admin=False
        )

        with app.app_context():
            db.session.add(u1)
            db.session.commit()

            # authenticate returns False if fails to authenticate
            self.assertNotEqual(User.authenticate(username, password), False)
