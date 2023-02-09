"""Models for reader"""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from open_library import fetch_book_data

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database"""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)

    bio = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Book(db.Model):
    """Book in the system."""

    __tablename__ = 'books'

    olid = db.Column(db.Text, primary_key=True)
    isbn = db.Column(db.Text, unique=True)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    cover_url = db.Column(db.Text) # if None uses font awesome icon

    def display_book(self):
        """Title by Author"""

        return f"{self.title} by {self.author}"

    def __repr__(self):
        return f"<Book {self.olid}: {self.title}, {self.author}>"
    
    def to_dict(self):
        """return a dict version of self to jsonify and send to client"""

        book_dict = {
            "olid" : self.olid,
            "isbn" : self.isbn,
            "title": self.title,
            "author": self.author,
            "cover_url": self.cover_url,
        }
        return book_dict
    
    @classmethod
    def create_book(cls, olid, isbn):
        """Fetch the relevant data and create a book"""

        fetched_data = fetch_book_data(olid)

        new_book = Book (
            olid = olid,
            isbn = isbn,
            title = fetched_data["title"],
            author = fetched_data.get("authors")[0] if "authors" in fetched_data else "Unknown",
            cover_url = fetched_data["cover_url"]
        )
        db.session.add(new_book)
        db.session.commit()

        return new_book


class BookNote(db.Model):
    """User's notes on a given Book"""

    __tablename__ = 'booknotes'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    book_olid = db.Column(
        db.Text,
        db.ForeignKey('books.olid', ondelete='CASCADE'),
        nullable=False,
    )

    read = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text)

    user = db.relationship("User", backref="notes")
    book = db.relationship("Book", backref="notes")


class BookList(db.Model):
    """User list of Books"""

    __tablename__ = 'booklists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    title = db.Column(db.Text)
    blurb = db.Column(db.Text)

    books = db.relationship("Book", secondary="booklist_books", backref="lists")
    user = db.relationship("User", backref="lists")


class BookListBooks(db.Model):
    """Booklist and book relations"""

    __tablename__ = 'booklist_books'

    booklist = db.Column(
        db.Integer,
        db.ForeignKey('booklists.id', ondelete='CASCADE'),
        primary_key=True,
    )

    book_olid = db.Column(
        db.Text,
        db.ForeignKey('books.olid', ondelete='CASCADE'),
        primary_key=True,
    )
