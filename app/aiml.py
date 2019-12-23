from app import pd, np, sm, smf, plt, Figure, FigureCanvas, send_file
from app.models import Match, User, Challenge
import io, base64


class Aiml(object):
    data_frame = None
    linear_model = None
    logistic_model = None

    def __init__(self):
        if Aiml.data_frame is not None:
            self.data_frame = Aiml.data_frame
        else:
            Aiml.data_frame = get_data_frame()
            self.data_frame = Aiml.data_frame
        self.linear_model = Aiml.linear_model
        self.logistic_model = Aiml.logistic_model



    def get_data_frame(self):
        return self.data_frame

    def get_correlation_matrix(self):
        if self.linear_model is None:
            x_data = self.data_frame[['resolved_challenge', 'challenger_won', 'left_hand', 'right_hand',
                                 'paddle_hard', 'paddle_soft', 'elo', 'wins', 'losses']]
            y_data = self.data_frame.winner_player_one
            self.linear_model = sm.OLS(y_data, x_data).fit()
            Aiml.linear_model = self.linear_model
        fig, ax = plt.subplots(figsize=(3,3))
        self.linear_model.predict()
        ax.matshow(self.data_frame.corr())
        ax.set_xticks(np.arange(self.data_frame.corr().shape[0]))
        ax.set_yticks(np.arange(self.data_frame.corr().shape[1]))
        ax.set_xticklabels(self.data_frame.corr().columns, fontsize=6, rotation=70)
        ax.set_yticklabels(self.data_frame.corr().columns, fontsize=6)
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        return send_file(img, mimetype='image/png')


    def get_confusion_matrix(self):
        if self.logistic_model is None:
            f = 'winner_player_one ~ resolved_challenge + challenger_won + left_hand + right_hand + paddle_hard + paddle_soft + elo + wins + losses'
            self.logistic_model = smf.logit(formula=str(f), data=self.data_frame).fit()
            Aiml.logistic_model = self.logistic_model
        matrix = self.logistic_model.pred_table(threshold=0.5)
        fig, ax = plt.subplots(figsize=(3,3))
        ax.matshow(matrix, cmap='seismic')
        x_headers = ('Guessed No', 'Guessed Yes')
        y_headers = ('Actual No', 'Actual Yes')
        ax.set_xticks(np.arange(matrix.shape[0]))
        ax.set_yticks(np.arange(matrix.shape[1]))
        ax.set_xticklabels(x_headers, rotation=45)
        ax.set_yticklabels(y_headers)
        for (i,j),z in np.ndenumerate(matrix):
            ax.text(j, i, '{:0.1f}'.format(z), ha='center', va='center')
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




