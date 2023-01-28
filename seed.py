"""Seed database"""

from app import db
from models import User


def seed_data(db):
    """Load the seed data"""

    db.drop_all()
    db.create_all()

    db.session.commit()
