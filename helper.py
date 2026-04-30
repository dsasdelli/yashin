def get_last_n_games(player_games_stats_df, player_id, last_n=5, start_timestamp=None):
    player_games_stats_df = player_games_stats_df[player_games_stats_df['playerId'] == player_id]
    player_games_stats_df = player_games_stats_df.sort_values(by='startTimestamp', ascending=False)
    if start_timestamp is not None:
        player_games_stats_df = player_games_stats_df[player_games_stats_df['startTimestamp'] < start_timestamp]
    return player_games_stats_df.head(last_n)

def get_players(player_games_stats_df, game_id, substitute=False):
    player_games_stats_df = player_games_stats_df[player_games_stats_df['gameId'] == game_id]
    player_games_stats_df = player_games_stats_df[player_games_stats_df['substitute'] == substitute]
    return player_games_stats_df['playerId'].tolist()

def get_starting_players(player_games_stats_df, game_id):
    return get_players(player_games_stats_df, game_id, substitute=False)

def get_substitute_players(player_games_stats_df, game_id):
    return get_players(player_games_stats_df, game_id, substitute=True)