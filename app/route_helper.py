from app import app
from app.models import User
from app.forms import ChallengeForm
from app.models import User, Match, Challenge


def _challenge_form_setter(challenger, challenged, form):
    form.challenger_name.data = challenger.name
    form.challenger_name.render_kw = {'disabled': 'disabled'}
    if challenger.is_lefty == 1 and challenger.is_righty == 1:
        form.challenger_handedness.data = 'ambidextrous'
    elif challenger.is_lefty == 1:
        form.challenger_handedness.data = 'left'
    else:
        form.challenger_handedness.data = 'right'
    if challenger.is_paddle_hard == 1 and challenger.is_paddle_soft == 1:
        form.challenger_paddle.data = 'both'
    elif challenger.is_paddle_soft == 1:
        form.challenger_paddle.data = 'soft'
    else:
        form.challenger_paddle.data = 'hard'
    form.challenger_elo.data = challenger.elo
    form.challenger_wins.data = challenger.wins
    form.challenger_losses.data = challenger.losses
    form.challenged_name.data = challenged.name
    form.challenged_name.render_kw = {'disabled': 'disabled'}
    if challenged.is_lefty == 1 and challenged.is_righty == 1:
        form.challenged_handedness.data = 'ambidextrous'
    elif challenged.is_lefty == 1:
        form.challenged_handedness.data = 'left'
    else:
        form.challenged_handedness.data = 'right'
    if challenged.is_paddle_hard == 1 and challenged.is_paddle_soft == 1:
        form.challenged_paddle.data = 'both'
    elif challenged.is_paddle_soft == 1:
        form.challenged_paddle.data = 'soft'
    else:
        form.challenged_paddle.data = 'hard'
    form.challenged_elo.data = challenged.elo
    form.challenged_wins.data = challenged.wins
    form.challenged_losses.data = challenged.losses


def _elo_calculator(winner, loser):
    winner_rating = 10**(winner.elo/400)
    loser_rating = 10**(loser.elo/400)
    winner_expected_score = winner_rating / (winner_rating + loser_rating)
    loser_expected_score = loser_rating / (loser_rating + winner_rating)
    winner_elo_change = 32 * (1 - winner_expected_score)
    loser_elo_change = 32 * (0 - loser_expected_score)
    winner.elo = User.elo + winner_elo_change
    loser.elo = User.elo + loser_elo_change


def _create_user(form):
    if form.handedness.data == 'ambidextrous':
        left_handed = 1
        right_handed = 1
    elif form.handedness.data == 'left':
        left_handed = 1
        right_handed = 0
    else:
        left_handed = 0
        right_handed = 1
    if form.paddle.data == 'both':
        hard_paddle=1
        soft_paddle=1
    elif form.paddle.data == 'soft':
        soft_paddle=1
        hard_paddle=0
    else:
        hard_paddle=1
        soft_paddle=0
    return User(email=form.email.data, name=form.name.data, is_lefty=left_handed, is_righty=right_handed,
                is_paddle_hard=hard_paddle, is_paddle_soft=soft_paddle)


def _get_unresolved_challenger_ids(user):
    unresolved_challengers = []
    unresolved_challenges = Challenge.query.filter_by(
        challenger_id=user.id, resolved_match_id=None).all()
    for challenge in unresolved_challenges:
        unresolved_challengers.append(challenge.challenged_id)
    unresolved_challenges = Challenge.query.filter_by(
        challenged_id=user.id, resolved_match_id=None).all()
    for challenge in unresolved_challenges:
        unresolved_challengers.append(challenge.challenger_id)
    return unresolved_challengers


def _resolve_challenge(winner, loser):
    unresolved_challenge = Challenge.query.filter_by(
        challenger_id=winner.id, challenged_id=loser.id, resolved_match_id=None).first()
    if unresolved_challenge is not None:
        return unresolved_challenge
    unresolved_challenge = Challenge.query.filter_by(
        challenger_id=loser.id, challenged_id=winner.id, resolved_match_id=None).first()
    if unresolved_challenge is not None:
        return unresolved_challenge
    return None
