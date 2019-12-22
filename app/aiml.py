from app import pd, np
from app.models import Match, User, Challenge


def _get_linear_regression_model():
    matches = Match.query.all()
    match_data = {'id': [],
                  'winner_player_one': [],
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
        player_one = User.query.filter_by(id=match.winner_id)
        player_two = User.query.filter_by(id=match.loser_id)
        match_data['id'].append(match.id)
        match_data['winner_player_one'].append(1)
        challenge = Challenge.query.filter_by(resolved_match_id=match.id)
        if challenge is not None:
            match_data['resolved_challenge'].append(1)
            if challenge.challenger_id == player_one.id:
                match_data['challenger_won'].append(1)
            else:
                match_data['challenger_won'].append(0)
        else:
            match_data['resolved_challenge'].append(0)
            match_data['challenger_won'].append(0)
        match_data['left_hand'].append(player_one.is_lefty - player_two.is_lefty)
        match_data['right_hand'].append(player_one.is_righty - player_two.is_righty)
        match_data['paddle_hard'].append(player_one.is_paddle_hard - player_two.is_paddle_hard)
        match_data['paddle_soft'].append(player_one.is_paddle_soft - player_two.is_paddle_soft)
        match_data['elo'].append(player_one.elo - player_two.elo)
        match_data['wins'].append(player_one.wins - player_two.wins)
        match_data['elo'].append(player_one.elo - player_two.elo)

    data_frame = pd.DataFrame(match_data)
    x_data = [['resolved_challenge', 'challenger_won', 'left_hand', 'right_hand',
               'paddle_hard', 'paddle_soft', 'elo', 'wins', 'losses']]
    y_data = match_data.winner_player_one
    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.33, random_state=12)
    model = LogisticRegression()
    model.fit(x_train, y_train)
    prediction = dict()
    prediction['Logistic'] = model.predict(x_test)
    print('Log: ', accuracy_score(y_test, prediction['Logistic']))
    print(model.coef_)
    conf_mat_logist = confusion_matrix(y_test, prediction['Logistic'])
    print('Logist \r', conf_mat_logist)









