import argparse
import pandas as pd

from helper import get_last_n_games, get_starting_players

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--inputFilePlayersGamesStats', help='input file players-games', default='games-players-processed/players_games_stats.csv')
parser.add_argument('-g', '--inputFileGamesStats', help='input file games', default='games-players-processed/games_stats.csv')

args = parser.parse_args()

games_stats_df = pd.read_csv(args.inputFileGamesStats)
players_games_stats_df = pd.read_csv(args.inputFilePlayersGamesStats)

for index, game in games_stats_df.iterrows():
    starting_players = get_starting_players(players_games_stats_df, game['gameId'])
    if (game['hasPlayerStatistics'] and game['hasGameStatistics']):
        for player_id in starting_players:
            last_n_games = get_last_n_games(players_games_stats_df, player_id, last_n=5, start_timestamp=game['startTimestamp'])
            if (last_n_games is not None and len(last_n_games) > 5):
                print(last_n_games['totalPass'])
                #print(f"Player ID: {player_id}, Last 5 Games: {last_n_games[['totalPasses']].to_dict(orient='records')}")
        print(f"Game ID: {game['gameId']}, Starting Players: {starting_players}")