"""we_connect/models.py."""
from flask_sqlalchemy import SQLAlchemy

from .run import app

# initialize sql-alchemy
db = SQLAlchemy(app)


class BaseModel(db.Model):
    """ Class is the base model """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,
                              onupdate=db.func.current_timestamp())


class User(BaseModel):
    """This class represents the user table."""

    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    logged_in_token = db.Column(db.String, default=None)
    businesses = db.relationship('Business', backref=backref('owner',
                uselist=False), cascade="all, delete-orphan", lazy=True)
    reviews = db.relationship('Review', backref=backref('owner',
                uselist=False), cascade="all, delete-orphan", lazy=True)

    @staticmethod
    def get_user(username_or_email):
        """Retrieve a user."""
        query1 = User.query.filter_by(username=username_or_email).first()
        query2 = User.query.filter_by(email=username_or_email).first()
        return query1 or query2


class Business(BaseModel):
    """This class represents the business table."""

    category = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    business_owner = db.Column(db.String, db.ForeignKey('user.username'))
    reviews = db.relationship('Review', backref=backref('review_for',
                uselist=False), cascade="all, delete-orphan", lazy=True)


class Review(BaseModel):
    """This class represents the review table."""

    rating = db.Column(db.Integer, nullable=False)
    body = db.Column(db.String, nullable=False)
    review_owner = db.Column(db.String, db.ForeignKey('user.username'))
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'))
