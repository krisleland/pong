from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    elo = db.Column(db.Float, index=True, unique=True)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    loser_id = db.Column(db.Integer, db.ForeignKey(User.id))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_challenge_id = db.Column(db.Integer)
    season = db.Column(db.Integer)
    winner = db.relationship('User', foreign_keys='Match.winner_id')
    loser = db.relationship('User', foreign_keys='Match.loser_id')


