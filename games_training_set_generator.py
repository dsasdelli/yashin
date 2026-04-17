import argparse
from pathlib import Path
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--inputFilePlayersGamesStats', help='input file players-games', default='games-players-processed/players_games_stats.csv')
parser.add_argument('-g', '--inputFileGamesStats', help='input file games', default='games-players-processed/games_stats.csv')

args = parser.parse_args()

games_stats_df = pd.read_csv(args.inputFileGamesStats)
players_games_stats_df = pd.read_csv(args.inputFilePlayersGamesStats)

for game in games_stats_df.itertuples():
    print(game)
    break

for player in players_games_stats_df.itertuples():
    print(player)
    break