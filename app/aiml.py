from app import pd, np, sm, smf, plt, Figure, FigureCanvas, send_file
from app.models import Match, User, Challenge
import io, base64
from app.forms import ChallengeForm


class Aiml(object):
    data_frame = None
    linear_model = None
    logistic_model = None

    def __init__(self):
        self.data_frame = self.build_data_frame() if Aiml.data_frame is None else Aiml.data_frame
        self.linear_model = self.build_linear_model() if Aiml.linear_model is None else Aiml.linear_model
        self.logistic_model = self.build_logistic_model() if Aiml.logistic_model is None else Aiml.logistic_model

    def get_data_frame(self):
        return self.data_frame

    def get_correlation_matrix(self):
        fig, ax = plt.subplots(num=2, figsize=(3, 3), clear=True)
        ax.matshow(self.data_frame.corr())
        ax.set_xticks(np.arange(self.data_frame.corr().shape[0]))
        ax.set_yticks(np.arange(self.data_frame.corr().shape[1]))
        ax.set_xticklabels(self.data_frame.corr().columns, fontsize=6, rotation=80)
        ax.set_yticklabels(self.data_frame.corr().columns, fontsize=6)
        img = io.BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        return img

    def get_confusion_matrix(self):
        matrix = self.logistic_model.pred_table(threshold=0.5)
        fig, ax = plt.subplots(num=1, figsize=(3, 3), clear=True)
        ax.matshow(matrix, cmap='seismic')
        x_headers = ('Guessed No', 'Guessed Yes')
        y_headers = ('Actual No', 'Actual Yes')
        ax.set_xticks(np.arange(matrix.shape[0]))
        ax.set_yticks(np.arange(matrix.shape[1]))
        ax.set_xticklabels(x_headers, rotation=45)
        ax.set_yticklabels(y_headers)
        for (i, j), z in np.ndenumerate(matrix):
            ax.text(j, i, '{:0.1f}'.format(z), ha='center', va='center')
        img = io.BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        return img

    def get_linear_model(self):
        return self.linear_model

    def get_logistic_model(self):
        return self.logistic_model

    def build_logistic_model(self):
        f = 'winner_player_one ~ player_one_challenger + player_two_challenger + player_one_left_hand + player_one_' \
            + 'right_hand +' \
            + 'player_two_left_hand + player_two_right_hand + player_one_paddle_hard' \
            + ' + player_one_paddle_soft + player_two_' \
            + 'paddle_hard + player_two_paddle_soft + elo + wins + losses'
        logistic_model = smf.logit(formula=str(f), data=self.data_frame).fit()
        Aiml.logistic_model = logistic_model
        return logistic_model

    def build_linear_model(self):
        x_data = self.data_frame[
            ['player_one_challenger', 'player_two_challenger', 'player_one_left_hand', 'player_one_right_hand',
             'player_two_left_hand', 'player_two_right_hand', 'player_one_paddle_hard', 'player_one_paddle_soft',
             'player_two_paddle_hard', 'player_two_paddle_soft', 'elo', 'wins', 'losses']]
        y_data = self.data_frame.winner_player_one
        linear_model = sm.OLS(y_data, x_data).fit()
        Aiml.linear_model = linear_model
        return linear_model

    def build_data_frame(self):
        matches = Match.query.all()
        match_data = {'winner_player_one': [],
                      'player_one_challenger': [],
                      'player_two_challenger': [],
                      'player_one_left_hand': [],
                      'player_one_right_hand': [],
                      'player_two_left_hand': [],
                      'player_two_right_hand': [],
                      'player_one_paddle_hard': [],
                      'player_one_paddle_soft': [],
                      'player_two_paddle_hard': [],
                      'player_two_paddle_soft': [],
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
                if challenge.challenger_id == player_one.id:
                    match_data['player_one_challenger'].append(1)
                    match_data['player_two_challenger'].append(0)
                else:
                    match_data['player_two_challenger'].append(1)
                    match_data['player_one_challenger'].append(0)
            else:
                match_data['player_one_challenger'].append(0)
                match_data['player_two_challenger'].append(0)
            match_data['player_one_left_hand'].append(
                player_one.is_lefty if player_one.is_lefty is not None else 0)
            match_data['player_one_right_hand'].append(
                player_one.is_righty if player_one.is_righty is not None else 0)
            match_data['player_two_left_hand'].append(
                player_two.is_lefty if player_two.is_lefty is not None else 0)
            match_data['player_two_right_hand'].append(
                player_two.is_righty if player_two.is_righty is not None else 0)
            match_data['player_one_paddle_hard'].append(
                player_one.is_paddle_hard if player_one.is_paddle_hard is not None else 0)
            match_data['player_one_paddle_soft'].append(
                player_one.is_paddle_soft if player_one.is_paddle_soft is not None else 0)
            match_data['player_two_paddle_hard'].append(
                player_two.is_paddle_hard if player_two.is_paddle_hard is not None else 0)
            match_data['player_two_paddle_soft'].append(
                player_two.is_paddle_soft if player_two.is_paddle_soft is not None else 0)
            match_data['elo'].append(player_one.elo - player_two.elo)
            match_data['wins'].append(player_one.wins if player_one.wins is not None else 0 -
                                                                                          player_two.is_wins if player_two.is_wins is not None else 0)
            match_data['losses'].append(player_one.losses if player_one.losses is not None else 0
                                                                                                - player_two.losses if player_two.losses is not None else 0)
        data_frame = pd.DataFrame(match_data)
        Aiml.data_frame = data_frame
        return data_frame

    def calculate_win_percent(self, challenger_form, challenged_form):
        match_data = {'player_one_challenger': [],
                      'player_two_challenger': [],
                      'player_one_left_hand': [],
                      'player_one_right_hand': [],
                      'player_two_left_hand': [],
                      'player_two_right_hand': [],
                      'player_one_paddle_hard': [],
                      'player_one_paddle_soft': [],
                      'player_two_paddle_hard': [],
                      'player_two_paddle_soft': [],
                      'elo': [],
                      'wins': [],
                      'losses': []}
        player_one = User.query.filter_by(name=challenger_form.challenger_name.data).first()
        player_two = User.query.filter_by(name=challenged_form.challenged_name.data).first()
        if Challenge.query.filter_by(challenger_id=player_one.id, challenged_id=player_two.id,
                                     resolved_match_id=None).first() is not None:
            match_data['player_one_challenger'].append(1)
            match_data['player_two_challenger'].append(0)
        elif Challenge.query.filter_by(challenger_id=player_two.id, challenged_id=player_two.id,
                                       resolved_match_id=None).first() is not None:
            match_data['player_two_challenger'].append(1)
            match_data['player_one_challenger'].append(0)
        else:
            match_data['player_one_challenger'].append(0)
            match_data['player_two_challenger'].append(0)
        if challenger_form.challenger_handedness.data == 'left' or challenger_form.challenger_handedness.data == 'ambidextrous':
            match_data['player_one_left_hand'].append(1)
        else:
            match_data['player_one_left_hand'].append(0)
        if challenger_form.challenger_handedness.data == 'right' or challenger_form.challenger_handedness.data == 'ambidextrous':
            match_data['player_one_right_hand'].append(1)
        else:
            match_data['player_one_right_hand'].append(0)
        if challenged_form.challenged_handedness.data == 'left' or challenged_form.challenged_handedness.data == 'ambidextrous':
            match_data['player_two_left_hand'].append(1)
        else:
            match_data['player_two_left_hand'].append(0)
        if challenged_form.challenged_handedness.data == 'right' or challenged_form.challenged_handedness.data == 'ambidextrous':
            match_data['player_two_right_hand'].append(1)
        else:
            match_data['player_two_right_hand'].append(0)
        if challenger_form.challenger_paddle.data == 'hard' or challenger_form.challenger_paddle.data == 'both':
            match_data['player_one_paddle_hard'].append(1)
        else:
            match_data['player_one_paddle_hard'].append(0)
        if challenger_form.challenger_paddle.data == 'soft' or challenger_form.challenger_paddle.data == 'both':
            match_data['player_one_paddle_soft'].append(1)
        else:
            match_data['player_one_paddle_soft'].append(0)
        if challenged_form.challenged_paddle.data == 'hard' or challenged_form.challenged_paddle.data == 'both':
            match_data['player_two_paddle_hard'].append(1)
        else:
            match_data['player_two_paddle_hard'].append(0)
        if challenged_form.challenged_paddle.data == 'soft' or challenged_form.challenged_paddle.data == 'both':
            match_data['player_two_paddle_soft'].append(1)
        else:
            match_data['player_two_paddle_soft'].append(0)
        match_data['elo'] = challenger_form.challenger_elo.data - challenged_form.challenged_elo.data
        match_data['wins'] = challenger_form.challenger_wins.data - challenged_form.challenged_wins.data
        match_data['losses'] = challenger_form.challenger_losses.data - challenged_form.challenged_losses.data
        df = pd.DataFrame(match_data)
        return self.linear_model.predict(df)