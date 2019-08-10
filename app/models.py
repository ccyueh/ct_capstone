from app import app, db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Party(db.Model): 
    party_id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    projected_start = db.Column(db.DateTime)
    projected_end = db.Column(db.DateTime)
    party_name = db.Column(db.String(100))
    location = db.Column(db.String(100))

    user = db.relationship('User', backref=db.backref('party', lazy='joined'))

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_img = db.Column(db.String(500))
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

class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer)
    description = db.Column(db.String(500))

class Characteristic(db.Model):
    characteristic_id = db.Column(db.Integer, primary_key=True
    characteristic_name = db.Column(db.String(50))

class PartyUser(db.Model):
    party_id = db.Column(db.Integer, db.ForeignKey('party.party_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    party = db.relationship('Party', backref=db.backref('party_user', lazy='joined'))
    user = db.relationship('User', backref=db.backref('party_user', lazy='joined'))

class PartyBottle(db.Model):
    party_id = db.Column(db.Integer, db.ForeignKey('party.party_id'))
    bottle_id = db.Column(db.Integer, db.ForeignKey('bottle.bottle_id'))

    party = db.relationship('Party', backref=db.backref('party_bottle', lazy='joined'))
    bottle = db.relationship('Bottle', backref=db.backref('party_bottle', lazy='joined'))

class BottleUser(db.Model):
    bottle_id = db.Column(db.Integer, db.ForeignKey('bottle.bottle_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    bottle = db.relationship('Bottle', backref=db.backref('bottle_user', lazy='joined'))
    user = db.relationship('User', backref=db.backref('bottle_user', lazy='joined'))

class RatingBottle(db.Model):
    rating_id = db.Column(db.Integer, db.ForeignKey('rating.rating_id'))
    bottle_id = db.Column(db.Integer, db.ForeignKey('bottle.bottle_id'))

    rating = db.relationship('Rating', backref=db.backref('rating_bottle', lazy='joined'))
    bottle = db.relationship('Bottle', backref=db.backref('rating_bottle', lazy='joined'))

class RatingUser(db.Model):
    rating_id = db.Column(db.Integer, db.ForeignKey('rating.rating_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    rating = db.relationship('Rating', backref=db.backref('rating_user', lazy='joined'))
    user = db.relationship('User', backref=db.backref('rating_user', lazy='joined'))

class RatingCharacteristic(db.Model):
    rating_id = db.Column(db.Integer, db.ForeignKey('rating.rating_id'))
    characteristic_id = db.Column(db.Integer, db.ForeignKey('characteristic.characteristic_id'))

    rating = db.relationship('Rating', backref=db.backref('rating_characteristic', lazy='joined'))
    characteristic = db.relationship('Characteristic', backref=db.backref('rating_characteristic', lazy='joined'))
