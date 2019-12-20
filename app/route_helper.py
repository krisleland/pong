from app import app
from app.models import User
from app.forms import ChallengeForm
from app.models import User, Match


def _challenge_form_setter(user, form):
    form.name.data = user.name
    form.name.render_kw = {'disabled': 'disabled'}
    if user.is_lefty == 1 and user.is_righty == 1:
        form.handedness.data = 'ambidextrous'
    elif user.is_lefty == 1:
        form.handedness.data = 'left'
    else:
        form.handedness.data = 'right'
    form.paddle.data = user.paddle_type
    form.elo.data = user.elo
    form.wins.data = user.wins
    form.losses.data = user.losses
    return form


def _elo_calculator(winner, loser):
    winner_rating = 10**(winner.elo/400)
    loser_rating = 10**(loser.elo/400)
    winner_expected_score = winner_rating / (winner_rating + loser_rating)
    loser_expected_score = loser_rating / (loser_rating + winner_rating)
    winner_elo_change = 32 * (1 - winner_expected_score)
    loser_elo_change = 32 * (1 - loser_expected_score)
    winner.elo = User.elo + winner_elo_change
    loser.elo = User.elo + loser_elo_change
