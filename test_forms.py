
import os
from unittest import TestCase
from sqlalchemy import exc
from app import app, do_login

from models import db, User, Book, BookNote, BookList

# Use test database and don't clutter tests with SQL
os.environ['DATABASE_URL'] = "postgresql:///olreader-test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

with app.app_context():
    db.drop_all()
    db.create_all()

def delete_all():
    """Helper method to clear the tables prior to testing"""
    
    Book.query.delete()
    BookNote.query.delete()
    BookList.query.delete()
    User.query.delete()

class AnonFormTest(TestCase):

    def setUp(self):
        """setup for each test"""
        self.client = app.test_client()

    def test_home(self):
        """Test the home page"""

        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<h2 class="join-message">', html)
            self.assertNotIn('<h2 class="welcome">', html)
    
    def test_signup(self):
        """Test the signup page"""

        with self.client:
            response = self.client.get('/signup')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<form method="POST" id="user_form">', html)
    
    def test_login(self):
        """Test the login page"""

        with self.client:
            response = self.client.get('/login')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<form method="POST" id="user_form">', html)
    
    def test_trending(self):
        """Test the browse page"""

        with self.client:
            response = self.client.get('/trending')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<div id="trending-recent"', html)
            self.assertIn('<div id="trending-popular"', html)
            self.assertIn('<div id="trending-monthly"', html)

    def test_search(self):
        """Test the search page"""

        with self.client:
            response = self.client.get('/search?term=watchmen')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn('<div id="search-results">', html)
            self.assertIn('watchmen', html)
