import pandas as pd

def get_team_last_n_games(games_stats_df, team_id, last_n=5, start_timestamp=None):
    if start_timestamp is not None:
        games_stats_df = games_stats_df[games_stats_df['startTimestamp'] < start_timestamp]
    last_n_games_stats_df = games_stats_df[(games_stats_df['homeTeamId'] == team_id) | (games_stats_df['awayTeamId'] == team_id)]
    last_n_games_stats_df = last_n_games_stats_df.sort_values(by='startTimestamp', ascending=False).head(last_n)
    last_n_games_stats_df.loc[(last_n_games_stats_df['homeTeamId'] == team_id), 'side'] = 'home'
    last_n_games_stats_df.loc[(last_n_games_stats_df['awayTeamId'] == team_id), 'side'] = 'away'
    return last_n_games_stats_df

def get_team_last_n_games_or_none(games_stats_df, team_id, last_n=5, start_timestamp=None, stack=True):
    last_n_games_stats_df = get_team_last_n_games(games_stats_df, team_id, last_n, start_timestamp).reset_index(drop=True)
    if (last_n_games_stats_df is not None and len(last_n_games_stats_df) == last_n):
        if (stack):
            last_n_games_stats_df.index = last_n_games_stats_df.index + 1
            last_n_games_stats_df = last_n_games_stats_df.stack()
            last_n_games_stats_df.index = last_n_games_stats_df.index.map('{0[1]}_p{0[0]}'.format)
            last_n_games_stats_df = last_n_games_stats_df.to_frame().T
        return last_n_games_stats_df
    return None

def get_player_last_n_games(player_games_stats_df, player_id, last_n=5, start_timestamp=None, substitute=False):
    player_games_stats_df = player_games_stats_df[player_games_stats_df['playerId'] == player_id]
    player_games_stats_df = player_games_stats_df.sort_values(by='startTimestamp', ascending=False)
    if start_timestamp is not None:
        player_games_stats_df = player_games_stats_df[(player_games_stats_df['startTimestamp'] < start_timestamp) & (player_games_stats_df['substitute'] == substitute)]
    return player_games_stats_df.head(last_n)

def get_players_last_n_games_or_none(players_games_stats_df, starting_players_ids, last_n, start_timestamp, stack=True, substitute=False):
    players_last_n_games_df_list = []
    for player_id in starting_players_ids:
        player_last_n_games_df_list = []
        player_last_n_games_df = get_player_last_n_games(players_games_stats_df, player_id, last_n=last_n, start_timestamp=start_timestamp, substitute=substitute)
        if (player_last_n_games_df is not None and len(player_last_n_games_df) == last_n):
            for i in range(len(player_last_n_games_df)):
                player_last_n_game_df = player_last_n_games_df.iloc[[i]]
                player_last_n_game_df = player_last_n_game_df.rename(columns=lambda x: x + f'_g{i}').reset_index(drop=True)
                player_last_n_games_df_list.append(player_last_n_game_df)
        else:
            return None
        players_last_n_games_df_list.append(pd.concat(player_last_n_games_df_list, axis=1))
    players_last_n_games_df = pd.concat(players_last_n_games_df_list, axis=0).reset_index(drop=True)
    if (stack):
        players_last_n_games_df.index = players_last_n_games_df.index + 1
        players_last_n_games_df = players_last_n_games_df.stack()
        players_last_n_games_df.index = players_last_n_games_df.index.map('{0[1]}_p{0[0]}'.format)
        players_last_n_games_df = players_last_n_games_df.to_frame().T
    return players_last_n_games_df

def get_players_ids_by_side(player_games_stats_df, game_id, side, substitute=False):
    player_games_stats_df = player_games_stats_df[(player_games_stats_df['gameId'] == game_id) & (player_games_stats_df['side'] == side) & (player_games_stats_df['substitute'] == substitute)]
    return player_games_stats_df['playerId'].tolist()

def get_starting_players_ids_by_side(player_games_stats_df, game_id, side):
    return get_players_ids_by_side(player_games_stats_df, game_id, side, substitute=False)

def get_substitute_players_ids(player_games_stats_df, game_id, side):
    return get_players_ids_by_side(player_games_stats_df, game_id, side, substitute=True)

def get_games_with_statistics(games_stats_df, player_statistics_required=True):
    if player_statistics_required:
        return games_stats_df[(games_stats_df['hasGameStatistics'] == True) & (games_stats_df['hasPlayerStatistics'] == True)]
    return games_stats_df[(games_stats_df['hasGameStatistics'] == True)]