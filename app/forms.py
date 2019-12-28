from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    handedness = SelectField(u'Dominate Hand', choices=[('left', 'Left'), ('right', 'Right'), ('ambidextrous', 'Ambidextrous')])
    paddle = SelectField(u'Paddle Type', choices=[('hard', 'Hard'), ('soft', 'Soft'), ('both', 'Both')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ChallengeForm(FlaskForm):
    challenger_name = StringField('Name')
    challenger_handedness = SelectField(u'Dominate Hand', choices=[('left', 'Left'), ('right', 'Right'), ('ambidextrous', 'Ambidextrous')])
    challenger_paddle = SelectField(u'Paddle Type', choices=[('hard', 'Hard'), ('soft', 'Soft'), ('both', 'Both')])
    challenger_elo = DecimalField('Elo')
    challenger_wins = IntegerField('Wins')
    challenger_losses = IntegerField('Losses')
    challenge_submit = SubmitField('Challenge')
    challenged_name = StringField('Name')
    challenged_handedness = SelectField('Dominate Hand', choices=[('left', 'Left'), ('right', 'Right'), ('ambidextrous', 'Ambidextrous')])
    challenged_paddle = SelectField(u'Paddle Type', choices=[('hard', 'Hard'), ('soft', 'Soft'), ('both', 'Both')])
    challenged_elo = DecimalField('Elo')
    challenged_wins = IntegerField('Wins')
    challenged_losses = IntegerField('Losses')
    challenge_calculate = SubmitField('Calculate Odds')
    descriptive_percent = StringField(u'Descriptive (logistic) prediction: ')
    descriptive_accuracy = StringField(u'Descriptive accuracy on test set: ')
    non_descriptive_percent = StringField(u'Non-Descriptive (neural-network) prediction: ')
    non_descriptive_accuracy = StringField(u'Non-Descriptive accuracy: ')


class MatchPostForm(FlaskForm):
    challenger = SelectField(u'Challenger', choices=[])
    win_or_lose = SelectField(u'Result', choices=[('win', 'Win'), ('lose', 'Lose')])
    submit = SubmitField(u'Post Match')
