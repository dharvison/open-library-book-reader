"""Seed database"""

from app import db
from models import User, Book, BookNote, BookList


def seed_data(db):
    """Load the seed data"""

    db.drop_all()
    db.create_all()

    db.session.commit()

    test_user = User.signup("davidh", "me@email.com", "welcome1")
    test_user.is_admin = True
    db.session.add(test_user)

    db.session.commit()

    l1 = BookList(
        title = "Sample List",
        blurb = "Description of the list",
        user_id = test_user.id,
    )

    l2 = BookList(
        title = "A Second List",
        blurb = "For when 1 list isn't enough!",
        user_id = test_user.id,
    )

    db.session.add_all([l1, l2])

    # dummy books
    b1 = Book(
        olid = "12345",
        title = "Watchmen",
        author = "Alan Moore",
        cover_url = "https://covers.openlibrary.org/b/id/6459694-S.jpg",
    )

    b2 = Book(
        olid = "11111",
        title = "Catch-22",
        author = "Joseph Heller",
        cover_url = "https://covers.openlibrary.org/b/id/13061725-S.jpg",
    )

    b3 = Book(
        olid = "22222",
        title = "Ulysses",
        author = "James Joyce",
        cover_url = "https://covers.openlibrary.org/b/id/13136659-S.jpg",
    )

    db.session.add_all([b1, b2, b3])
    db.session.commit()
