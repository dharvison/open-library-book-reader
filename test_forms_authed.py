
import os
from unittest import TestCase
from sqlalchemy import exc
from app import app
from flask import session, json

from models import db, User, Book, BookNote, BookList
from seed import seed_data

# Use test database and don't clutter tests with SQL
os.environ['DATABASE_URL'] = "postgresql:///olreader-test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Disable CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

with app.app_context():
    db.drop_all()
    db.create_all()
    seed_data(db)


class LoggedInFormTest(TestCase):
    """Tests with logged in user"""

    def setUp(self):
        """setup for each test"""
        self.client = app.test_client()

    def login_for_test(self):
        """helper method to login"""

        response = self.client.post('/login', data={'username': 'testuser', 'password': 'welcome1'}, follow_redirects=True)
        user = User.query.filter_by(username='testuser').one()
        self.user_id = user.id
        self.assertEqual(response.status_code, 200)



class LoginTest(TestCase):
    """Test Login"""

    def setUp(self):
        """setup for each test"""
        self.client = app.test_client()

    def test_login(self):
        """Test the login page"""

        with self.client:
            response = self.client.post('/login', data={'username': 'testuser', 'password': 'welcome1'}, follow_redirects=True)
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('<h2 class="join-message">', html)
            self.assertIn('<h2 class="welcome">', html)



class NoteTest(LoggedInFormTest):
    """Tests for Notes"""

    def test_create_note(self):
        """Test note creation"""

        with self.client:
            self.login_for_test()
            response = self.client.post('/notes/create', data={'book_olid': '12345', 'note': 'Test Note', 'read': True}, follow_redirects=True)
            # check HTML
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('<a href="/books/12345"', html)
            self.assertIn('<p class="note-text">Test Note</p>', html)
            # check the DB
            note = BookNote.query.filter_by(user_id=self.user_id).first()
            self.assertEqual(note.book_olid, '12345')
            self.assertEqual(note.note, 'Test Note')
            self.assertEqual(note.read, True)

    def test_view_note(self):
        """Test view note"""

        with self.client:
            self.login_for_test()
            note = BookNote.query.filter_by(user_id=self.user_id).first()

            response = self.client.get(f'/notes/{note.id}')
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(f'<a href="/books/{note.book_olid}"', html)
            self.assertIn(f'<p class="note-text">{note.note}</p>', html)
    
    def test_edit_note(self):
        """Test edit note"""

        with self.client:
            self.login_for_test()
            note = BookNote.query.filter_by(user_id=self.user_id).first()
            prev_note = note.note

            response = self.client.post(f'/notes/{note.id}/edit', data={'note': 'Updated Note', 'read': True}, follow_redirects=True)
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(f'<a href="/books/{note.book_olid}"', html)
            self.assertIn('<p class="note-text">Updated Note</p>', html)
            # check the DB
            note = BookNote.query.filter_by(user_id=self.user_id).filter_by(book_olid=note.book_olid).one()
            self.assertNotEqual(note.note, prev_note)
            self.assertEqual(note.note, 'Updated Note')

    def test_create_note_fetch(self):
        """Test note creation for book not in DB"""

        with self.client:
            self.login_for_test()
            fetch_olid = 'OL63073W'
            # This book doesn't exist in DB
            no_book = Book.query.filter_by(olid=fetch_olid).one_or_none()
            self.assertIsNone(no_book)

            # Create a note which results in fetching the book
            response = self.client.post('/notes/create', data={'book_olid': fetch_olid, 'note': 'Testing Ernest', 'read': True}, follow_redirects=True)
            # check HTML
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('<a href="/books/OL63073W"', html)
            self.assertIn('<p class="note-text">Testing Ernest</p>', html)
            # check the DB for note
            note = BookNote.query.filter_by(user_id=self.user_id).filter_by(book_olid=fetch_olid).one()
            self.assertEqual(note.book_olid, fetch_olid)
            self.assertEqual(note.note, 'Testing Ernest')
            self.assertEqual(note.read, True)
            # check DB that book was fetched
            book = Book.query.filter_by(olid=fetch_olid).one()
            self.assertIsNotNone(book)



class ListTest(LoggedInFormTest):
    """Tests for Lists"""

    def test_create_list(self):
        """Test list creation"""

        with self.client:
            self.login_for_test()
            response = self.client.post('/lists/create', data={'title': 'Test List', 'blurb': 'a test list'}, follow_redirects=True)
            # check html
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Test List', html)
            self.assertIn('<p>a test list</p>', html)
            self.assertIn('<div id="booklist-books"', html)
            # no books have been added
            self.assertNotIn('<div class="list-book">', html)
            # check DB
            bl = BookList.query.filter_by(user_id=self.user_id).first()
            self.assertEqual(bl.title, 'Test List')
            self.assertEqual(bl.blurb, 'a test list')

    def test_edit_list(self):
        """Test list edit"""

        with self.client:
            self.login_for_test()
            bl = BookList.query.filter_by(user_id=self.user_id).first()
            prev_title = bl.title
            prev_blurb = bl.blurb

            response = self.client.post(f'/lists/{bl.id}/edit', data={'title': 'Updated List', 'blurb': 'changed text!'}, follow_redirects=True)
            # check html
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Updated List', html)
            self.assertIn('<p>changed text!</p>', html)
            self.assertIn('<div id="booklist-books"', html)
            # check DB
            bl = BookList.query.filter_by(user_id=self.user_id).first()
            self.assertNotEqual(bl.title, prev_title)
            self.assertNotEqual(bl.blurb, prev_blurb)
            self.assertEqual(bl.title, 'Updated List')
            self.assertEqual(bl.blurb, 'changed text!')

    def test_list_add(self):
        """Test list add book"""

        with self.client:
            self.login_for_test()
            bl = BookList.query.filter_by(user_id=self.user_id).first()
            prev_len = len(bl.books)
            book = Book.query.filter_by(olid='12345').one()

            response = self.client.post(f'/lists/{bl.id}/add', json={'workId': book.olid, 'isbn': book.isbn}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # check json
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['author'], book.author)
            self.assertEqual(data['title'], book.title)
            self.assertEqual(data['olid'], book.olid)
            self.assertEqual(data['isbn'], book.isbn)
            self.assertEqual(data['cover_url'], book.cover_url)
            # check DB
            bl = BookList.query.filter_by(id=bl.id).one()
            self.assertEqual(len(bl.books), prev_len + 1)
            self.assertEqual(bl.books[0].olid, book.olid)

    def test_list_add_dup(self):
        """Test list add book again"""

        with self.client:
            self.login_for_test()
            bl = BookList.query.filter_by(user_id=self.user_id).first()
            prev_len = len(bl.books)
            book = Book.query.filter_by(olid='12345').one()

            response = self.client.post(f'/lists/{bl.id}/add', json={'workId': book.olid, 'isbn': book.isbn}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # check json
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['err'], f"List already contains {book.title}")
            # check DB
            bl = BookList.query.filter_by(id=bl.id).one()
            self.assertEqual(len(bl.books), prev_len)
            self.assertEqual(bl.books[0].olid, book.olid)
    
    def test_list_remove(self):
        """Test remove book"""

        with self.client:
            self.login_for_test()
            bl = BookList.query.filter_by(user_id=self.user_id).first()
            prev_len = len(bl.books)
            book = Book.query.filter_by(olid='12345').one()

            response = self.client.post(f'/lists/{bl.id}/remove', json={'workId': book.olid, 'isbn': book.isbn}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # check json
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['result'], "success")
            # check DB
            bl = BookList.query.filter_by(id=bl.id).one()
            self.assertEqual(len(bl.books), prev_len - 1)
    
    def test_list_remove_not_in_list(self):
        """Test remove a book not in the list"""

        with self.client:
            self.login_for_test()
            bl = BookList.query.filter_by(user_id=self.user_id).first()
            cur_length = len(bl.books)
            book = Book.query.filter_by(olid='11111').one()

            response = self.client.post(f'/lists/{bl.id}/remove', json={'workId': book.olid, 'isbn': book.isbn}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # check json
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['err'], f"{book.title} isn't in this list.")
            # check DB
            bl = BookList.query.filter_by(id=bl.id).one()
            self.assertEqual(len(bl.books), cur_length)

    def test_list_add_fetch(self):
        """Test list add for book not in DB"""

        with self.client:
            self.login_for_test()
            fetch_olid = 'OL679333W'
            # This book doesn't exist in DB
            no_book = Book.query.filter_by(olid=fetch_olid).one_or_none()
            self.assertIsNone(no_book)

            bl = BookList.query.filter_by(user_id=self.user_id).first()
            prev_len = len(bl.books)
            response = self.client.post(f'/lists/{bl.id}/add', json={'workId': fetch_olid, 'isbn': ''}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # check json
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['olid'], fetch_olid)
            # check DB
            bl = BookList.query.filter_by(id=bl.id).one()
            self.assertEqual(len(bl.books), prev_len + 1)
            # check DB that book was fetched
            book = Book.query.filter_by(olid=fetch_olid).one()
            self.assertIsNotNone(book)



class BookTest(LoggedInFormTest):
    """Tests for Books"""

    def test_book_view(self):
        """Test view book"""

        with self.client:
            self.login_for_test()
            book = Book.query.filter_by(olid='OL86318W').one()

            response = self.client.get(f'/books/{book.olid}')
            # check HTML
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(book.title, html)
            self.assertIn(book.author, html)
            self.assertIn(f'<a href="/books/{book.olid}" class="link-dark link-title">{book.title}</a>', html)
            self.assertIn(f'<img class="my-3" src="{book.cover_url}-M.jpg" alt="cover"/>', html)
            self.assertIn(f'<a href="https://openlibrary.org/works/{book.olid}"', html)
