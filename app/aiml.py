from app import pd, np, sm, smf, plt, Figure, FigureCanvas, send_file, LinearRegression, train_test_split
from app import KNeighborsClassifier, accuracy_score, KMeans, MLPClassifier, LogisticRegression, confusion_matrix
from app.models import Match, User, Challenge
import io, base64
from app.forms import ChallengeForm


class Aiml(object):
    data_frame = None
    neural_model = None
    logistic_model = None
    x_train = None
    x_test = None
    y_train = None
    y_test = None

    def __init__(self):
        self.data_frame = self.build_data_frame()
        self.x_train, self.x_test, self.y_train, self.y_test = self.build_training_data()
        self.logistic_model = self.build_logistic_model()
        self.neural_model = self.build_neural_model()

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
        matrix = confusion_matrix(self.y_test, self.logistic_model.predict(self.x_test))
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

    def get_logistic_model(self):
        return self.logistic_model

    def build_logistic_model(self):
        log = LogisticRegression().fit(self.x_train, self.y_train)
        log_pred = log.predict(self.x_test)
        print("Logistic Model accuracy score : ", accuracy_score(self.y_test, log_pred))
        return log

    def build_neural_model(self):
        neural_model = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(10, 2), random_state=1,
                            max_iter=10000000000000)
        neural_model.fit(self.x_train, self.y_train)
        neural_pred = neural_model.predict(self.x_test)
        print("Neural Model accuracy score : ", accuracy_score(self.y_test, neural_pred))
        return neural_model

    def build_training_data(self):
        if self.data_frame is None:
            self.build_data_frame()
        x_data = self.data_frame[
            ['player_one_challenger', 'player_two_challenger', 'player_one_left_hand', 'player_one_right_hand',
             'player_two_left_hand', 'player_two_right_hand', 'player_one_paddle_hard', 'player_one_paddle_soft',
             'player_two_paddle_hard', 'player_two_paddle_soft', 'elo', 'wins', 'losses']]
        y_data = self.data_frame.winner_player_one
        x_train, x_test, y_train, y_test = train_test_split(
            x_data, y_data, test_size=0.33, random_state=42)
        return x_train, x_test, y_train, y_test

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

    def calculate_win_percent(self, player_one, player_two):
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
        if player_one.is_lefty == 1:
            match_data['player_one_left_hand'].append(1)
        else:
            match_data['player_one_left_hand'].append(0)
        if player_one.is_righty == 1:
            match_data['player_one_right_hand'].append(1)
        else:
            match_data['player_one_right_hand'].append(0)
        if player_two.is_lefty == 1:
            match_data['player_two_left_hand'].append(1)
        else:
            match_data['player_two_left_hand'].append(0)
        if player_two.is_righty == 1:
            match_data['player_two_right_hand'].append(1)
        else:
            match_data['player_two_right_hand'].append(0)
        if player_one.is_paddle_hard == 1:
            match_data['player_one_paddle_hard'].append(1)
        else:
            match_data['player_one_paddle_hard'].append(0)
        if player_one.is_paddle_soft == 1:
            match_data['player_one_paddle_soft'].append(1)
        else:
            match_data['player_one_paddle_soft'].append(0)
        if player_two.is_paddle_hard == 1:
            match_data['player_two_paddle_hard'].append(1)
        else:
            match_data['player_two_paddle_hard'].append(0)
        if player_two.is_paddle_soft == 1:
            match_data['player_two_paddle_soft'].append(1)
        else:
            match_data['player_two_paddle_soft'].append(0)
        match_data['elo'] = player_one.elo - player_two.elo
        match_data['wins'] = player_one.wins - player_two.wins
        match_data['losses'] = player_one.losses - player_two.losses
        df = pd.DataFrame(match_data)
        logistic_challenger_win = self.logistic_model.predict(df)
        if logistic_challenger_win[0] == 0:
            logistic_message = "Player one does not win"
        else:
            logistic_message = "Player one does win"
        neural_challenger_win = self.neural_model.predict(df)
        if neural_challenger_win[0] == 0:
            neural_message = "Player one does not win"
        else:
            neural_message = "Player one does win"
        return (logistic_message, accuracy_score(self.y_test, self.logistic_model.predict(self.x_test)),
                neural_message, accuracy_score(self.y_test, self.neural_model.predict(self.x_test)))