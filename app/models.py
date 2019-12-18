from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    handedness = db.Column(db.String(64), index=True)
    paddle_type = db.Column(db.String(64), index=True)
    elo = db.Column(db.Float, index=True, default=1500.000)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

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


