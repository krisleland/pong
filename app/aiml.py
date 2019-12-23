from app import pd, np, sm, smf, plt, Figure, FigureCanvas, send_file
from app.models import Match, User, Challenge
import io, base64


class Aiml(object):
    data_frame = None

    def __init__(self):
        if Aiml.data_frame is not None:
            self.data_frame = Aiml.data_frame
        else:
            Aiml.data_frame = get_data_frame()
            self.data_frame = Aiml.data_frame


    def get_data_frame(self):
        return self.data_frame


def set_frame_data(data_frame):
    x_data = data_frame[['resolved_challenge', 'challenger_won', 'left_hand', 'right_hand',
                         'paddle_hard', 'paddle_soft', 'elo', 'wins', 'losses']]
    y_data = data_frame.winner_player_one
    model = sm.OLS(y_data, x_data).fit()


def get_correlation_matrix(data_frame):
    x_data = data_frame[['resolved_challenge', 'challenger_won', 'left_hand', 'right_hand',
                         'paddle_hard', 'paddle_soft', 'elo', 'wins', 'losses']]
    y_data = data_frame.winner_player_one
    model = sm.OLS(y_data, x_data).fit()
    plt.figure(figsize=(3,3))
    plt.matshow(data_frame.corr(), fignum=1)
    plt.xticks(range(data_frame.shape[1]), data_frame.columns, fontsize=6, rotation=70)
    plt.yticks(range(data_frame.shape[1]), data_frame.columns, fontsize=8)
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return send_file(img, mimetype='image/png')


def get_confusion_matrix(data_frame):
    f = 'winner_player_one ~ resolved_challenge + challenger_won + left_hand + right_hand + paddle_hard + paddle_soft + elo + wins + losses'
    res = smf.logit(formula=str(f), data=data_frame).fit()
    plt.figure(figsize=(3,3))
    plt.matshow(res.pred_table(), fignum=3)
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return send_file(img, mimetype='image/png')


def get_data_frame():
    matches = Match.query.all()
    match_data = {'winner_player_one': [],
                  'resolved_challenge': [],
                  'challenger_won': [],
                  'left_hand': [],
                  'right_hand': [],
                  'paddle_hard': [],
                  'paddle_soft': [],
                  'elo': [],
                  'wins': [],
                  'losses': []}
    for match in matches:
        if match.id % 2 == 0:
            player_one = User.query.filter_by(id=match.winner_id).first()
            player_two = User.query.filter_by(id=match.loser_id).first()
            match_data['winner_player_one'].append(1)
        else:
            player_one = User.query.filter_by(id=match.loser_id).first()
            player_two = User.query.filter_by(id=match.winner_id).first()
            match_data['winner_player_one'].append(0)
        challenge = Challenge.query.filter_by(resolved_match_id=match.id).first()
        if challenge is not None:
            match_data['resolved_challenge'].append(1)
            if challenge.challenger_id == player_one.id:
                match_data['challenger_won'].append(1)
            else:
                match_data['challenger_won'].append(0)
        else:
            match_data['resolved_challenge'].append(0)
            match_data['challenger_won'].append(0)
        if player_one.is_lefty is None:
            player_one.is_lefty = 0

        match_data['left_hand'].append(
            player_one.is_lefty if player_one.is_lefty is not None else 0 - player_two.is_lefty if player_two.is_lefty is not None else 0)
        match_data['right_hand'].append(
            player_one.is_righty if player_one.is_righty is not None else 0 - player_two.is_righty if player_two.is_righty is not None else 0)
        match_data['paddle_hard'].append(player_one.is_paddle_hard if player_one.is_paddle_hard is not None else 0 -
                                                                                                                 player_two.is_paddle_hard if player_two.is_paddle_hard is not None else 0)
        match_data['paddle_soft'].append(player_one.is_paddle_soft if player_one.is_paddle_soft is not None else 0 -
                                                                                                                 player_two.is_paddle_soft if player_two.is_paddle_soft is not None else 0)
        match_data['elo'].append(player_one.elo - player_two.elo)
        match_data['wins'].append(
            player_one.wins if player_one.wins is not None else 0 - player_two.is_wins if player_two.is_wins is not None else 0)
        match_data['losses'].append(
            player_one.losses if player_one.losses is not None else 0 - player_two.losses if player_two.losses is not None else 0)

    data_frame = pd.DataFrame(match_data)
    return data_frame




