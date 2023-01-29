"""Models for reader"""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

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

    # image_url = db.Column(
    #     db.Text,
    #     default="/static/images/default-pic.png",
    # )

    # header_image_url = db.Column(
    #     db.Text,
    #     default="/static/images/warbler-hero.jpg"
    # )

    bio = db.Column(db.Text)
    location = db.Column(db.Text)
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

    isbn = db.Column(db.Text, primary_key=True)

    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    cover_url = db.Column(db.Text) # Need a default blank cover
    # else needs to be cached?

    def display_book(self):
        """Title by Author"""

        return f"{self.title} by {self.author}"

    def __repr__(self):
        return f"<Book #{self.isbn}: {self.title}, {self.author}>"


class BookNote(db.Model):
    """User's notes on a given Book"""

    __tablename__ = 'booknotes'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    book_isbn = db.Column(
        db.Text,
        db.ForeignKey('books.isbn', ondelete='CASCADE'),
        nullable=False,
    )

    read = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text)

    user = db.relationship("User", backref="notes")
    book = db.relationship("Book") # probably don't need link from Book to Notes


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

    book_isbn = db.Column(
        db.Text,
        db.ForeignKey('books.isbn', ondelete='CASCADE'),
        primary_key=True,
    )
