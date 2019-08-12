from app import app, db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

party_guests = db.Table('party_guests',
db.Column('party_id', db.Integer, db.ForeignKey('party.party_id')),
db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'))
)

rating_characteristics = db.Table('rating_characteristics',
db.Column('rating_id', db.Integer, db.ForeignKey('rating.rating_id')),
db.Column('characteristic_id', db.Integer, db.ForeignKey('characteristic.characteristic_id'))
)

class Party(db.Model):
    party_id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    party_name = db.Column(db.String(100))
    location = db.Column(db.String(100))

    host_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', backref=db.backref('party', lazy='joined'))

    guests = db.relationship('User', secondary=party_guests, backref='party_guests')

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    #profile_img = db.Column(db.String(500))
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Bottle(db.Model):
    bottle_id = db.Column(db.Integer, primary_key=True)
    producer = db.Column(db.String(100))
    bottle_name = db.Column(db.String(100))
    vintage = db.Column(db.Integer)
    label_img = db.Column(db.String(500))

    party_id = db.Column(db.Integer, db.ForeignKey('party.party_id'))
    party = db.relationship('Party', backref=db.backref('bottle', lazy='joined'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', backref=db.backref('bottle', lazy='joined'))

class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer)
    description = db.Column(db.String(500))

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', backref=db.backref('rating', lazy='joined'))

    bottle_id = db.Column(db.Integer, db.ForeignKey('bottle.bottle_id'))
    bottle = db.relationship('Bottle', backref=db.backref('rating', lazy='joined'))

    characteristics = db.relationship('Characteristic', secondary=rating_characteristics, backref='rating_notes')

class Characteristic(db.Model):
    characteristic_id = db.Column(db.Integer, primary_key=True)
    characteristic_name = db.Column(db.String(50))
