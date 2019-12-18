from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    elo = db.Column(db.String(120), index=True, unique=True)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    date_added = db.Column(db.DATETIME, timezone=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)


