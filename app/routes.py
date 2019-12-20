from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, ChallengeForm
from flask_login import current_user, login_user, logout_user
from app.models import User
from werkzeug.urls import url_parse
from app.route_helper import _challenge_form_setter


@app.route('/')
@app.route('/index')
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
    else:
        challenge_players = []
    return render_template('index.html', title='Home', players=players, challenge_players=challenge_players)


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
        user = User(email=form.email.data, name=form.name.data, handedness=form.handedness.data,
                    paddle_type=form.paddle.data)
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
    challenger_form = ChallengeForm()
    challenged_form = ChallengeForm()
    challenger_form = _challenge_form_setter(current_user, challenger_form)
    challenged_form = _challenge_form_setter(challenged_user, challenged_form)
    return render_template('challenge.html', title='Challenge', challenger_form=challenger_form, challenged_form=challenged_form)

