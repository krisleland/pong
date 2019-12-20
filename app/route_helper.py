from app import app
from app.models import User
from app.forms import ChallengeForm


def _challenge_form_setter(user, form):
    form.name.data = user.name
    form.name.render_kw = {'disabled': 'disabled'}
    form.handedness.data = user.handedness
    form.paddle.data = user.paddle_type
    form.elo.data = user.elo
    form.wins.data = user.wins
    form.losses.data = user.losses
    return form
