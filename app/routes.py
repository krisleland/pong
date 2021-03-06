from flask import render_template, flash, redirect, url_for, request, Response
from app import app, db, Figure, FigureCanvas
from app.forms import LoginForm, RegistrationForm, ChallengeForm, MatchPostForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Match, Challenge
from werkzeug.urls import url_parse
from werkzeug import FileWrapper
from app.route_helper import _challenge_form_setter, _elo_calculator, _create_user, _get_unresolved_challenger_ids
from app.route_helper import _resolve_challenge
from app.aiml import Aiml
import io


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    players = User.query.order_by(User.elo.desc()).all()
    if current_user.is_authenticated:
        index = players.index(current_user)
        low_index = index-2
        if low_index < 0:
            low_index = 0
        high_index = index+3
        if high_index > len(players):
            high_index = len(players)
        challenge_players = players[low_index:high_index]
        unresolved_challengers = _get_unresolved_challenger_ids(current_user)
        Aiml().get_logistic_model()
    else:
        challenge_players = []
        unresolved_challengers = []
    return render_template('index.html', title='Home', players=players, challenge_players=challenge_players,
                           unresolved_challenges=unresolved_challengers)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = _create_user(form)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/challenge/<challenged_id>', methods=['GET', 'POST'])
def challenge(challenged_id):
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    challenged_user = User.query.get(challenged_id)
    challenger_user = User.query.get(current_user.id)
    form = ChallengeForm()

    if form.challenge_submit.data:
        challenge = Challenge(challenger_id=current_user.id,
                              challenged_id=challenged_user.id,
                              resolved_match_id=None)
        db.session.add(challenge)
        db.session.commit()
        flash('You have challenged {player}!'.format(player=challenged_user.name))
        return redirect(url_for('index'))
    elif form.challenge_calculate.data:
        if form.challenger_handedness.data == 'ambidextrous':
            challenger_user.is_lefty = 1
            challenger_user.is_righty = 1
        elif form.challenger_handedness.data == 'left':
            challenger_user.is_lefty = 1
            challenger_user.is_righty = 0
        else:
            challenger_user.is_lefty = 0
            challenger_user.is_righty = 1
        if form.challenged_handedness.data == 'ambidextrous':
            challenged_user.is_lefty = 1
            challenged_user.is_righty = 1
        elif form.challenged_handedness.data == 'left':
            challenged_user.is_lefty = 1
            challenged_user.is_righty = 0
        else:
            challenged_user.is_lefty = 0
            challenged_user.is_righty = 1
        if form.challenger_paddle.data == 'both':
            challenger_user.is_paddle_hard = 1
            challenger_user.is_paddle_soft = 1
        elif form.challenger_paddle.data == 'soft':
            challenger_user.is_paddle_soft = 1
            challenger_user.is_paddle_hard = 0
        else:
            challenger_user.is_paddle_hard = 1
            challenger_user.is_paddle_soft = 0
        if form.challenged_paddle.data == 'both':
            challenged_user.is_paddle_hard = 1
            challenged_user.is_paddle_soft = 1
        elif form.challenged_paddle.data == 'soft':
            challenged_user.is_paddle_soft = 1
            challenged_user.is_paddle_hard = 0
        else:
            challenged_user.is_paddle_hard = 1
            challenged_user.is_paddle_soft = 0
        challenger_user.elo = float(form.challenger_elo.data)
        challenged_user.elo = float(form.challenged_elo.data)
        challenger_user.wins = int(form.challenger_wins.data)
        challenged_user.wins = int(form.challenged_wins.data)
        challenger_user.losses = int(form.challenger_losses.data)
        challenged_user.losses = int(form.challenged_losses.data)
        db.session.commit()
        return redirect(url_for('challenge', challenged_id=challenged_user.id))
    _challenge_form_setter(challenger_user, challenged_user, form)
    form.descriptive_percent.data, form.descriptive_accuracy.data, form.non_descriptive_percent.data, \
        form.non_descriptive_accuracy.data = Aiml().calculate_win_percent(challenger_user, challenged_user)
    flash('Changes to user data are permanent.  Edit stats and click "Calculate Odds" to '
          'get a new calculated chance to win.  Models are re-trained.')
    return render_template('challenge.html', title='Challenge', form=form)


@app.route('/post/<challenged_id>', methods=['GET', 'POST'])
@app.route('/post', methods=['GET', 'POST'])
def post(challenged_id=None):
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    players = User.query.order_by(User.name)
    post_form = MatchPostForm()
    for player in players:
        post_form.challenger.choices += [(player.name, player.name.capitalize())]
    if challenged_id is not None:
        challenged_player = User.query.filter_by(id=challenged_id).first()
        post_form.challenger.data = challenged_player.name
    if post_form.validate_on_submit():
        if post_form.win_or_lose.data == 'win':
            winner = current_user
            loser = User.query.filter_by(name=post_form.challenger.data).first()
        else:
            winner = User.query.filter_by(name=post_form.challenger.data).first()
            loser = current_user
        resolve_challenge = _resolve_challenge(winner, loser)
        if resolve_challenge is not None:
            match = Match(winner_id=winner.id, loser_id=loser.id, resolved_challenge_id=resolve_challenge.id)
        else:
            match = Match(winner_id=winner.id, loser_id=loser.id)
        _elo_calculator(winner, loser)
        db.session.add(match)
        db.session.commit()
        if resolve_challenge is not None:
            resolve_challenge.resolved_match_id = match.id
        winner.wins = User.wins + 1
        loser.losses = User.losses + 1
        db.session.commit()
        flash('Match successfully posted!')
        return redirect(url_for('index'))
    return render_template('post.html', form=post_form)


@app.route('/corr_matrix.png', methods=['GET', 'POST'])
def corr_matrix_png():
    matrix = Aiml().get_correlation_matrix()
    w = FileWrapper(matrix)
    return Response(w, mimetype='img/png', direct_passthrough=True)


@app.route('/confusion_matrix.png', methods=['GET', 'POST'])
def confusion_matrix_png():
    matrix = Aiml().get_confusion_matrix()
    w = FileWrapper(matrix)
    return Response(w, mimetype='img/png', direct_passthrough=True)

@app.route('/coef_graph.png', methods=['GET', 'POST'])
def coef_graph_png():
    graph = Aiml().get_coef_graph()
    w = FileWrapper(graph)
    return Response(w, mimetype='img/png', direct_passthrough=True)