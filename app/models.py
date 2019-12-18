from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Hand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hand = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<{} Hand>'.format(self.hand)


class Paddle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hardness = db.Column(db.String(64))

    def __repr__(self):
        return '<{} Paddle>'.format(self.hardness)


class User(Usermixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(60), index=True)
    handedness = db.Column(db.Integer, db.ForeignKey(Hand.id), index=True)
    paddle_type = db.Column(db.Integer, db.ForeignKey(Paddle.id), index=True)
    elo = db.Column(db.Float, index=True, unique=True, default=1500.000)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    hand = db.relationship('Hand', foreign_keys='User.handedness')
    paddle = db.relationship('Paddle', foreign_keys='User.paddle_type')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    loser_id = db.Column(db.Integer, db.ForeignKey(User.id))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_challenge_id = db.Column(db.Integer)
    season = db.Column(db.Integer)
    winner = db.relationship('User', foreign_keys='Match.winner_id')
    loser = db.relationship('User', foreign_keys='Match.loser_id')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


