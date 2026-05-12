import argparse
from pathlib import Path
import pandas as pd

from helper import get_team_last_n_games_or_none, get_games_with_statistics

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--inputFilePlayersGamesStats', help='input file players-games', default='games-players-processed/players_games_stats.csv')
parser.add_argument('-g', '--inputFileGamesStats', help='input file games', default='games-players-processed/games_stats.csv')
parser.add_argument('-o', '--outputDir', help='output directory', default='games-players-processed')
parser.add_argument('-l', '--lastNGames', type=int, help='last n games to consider', default=5)

args = parser.parse_args()

games_stats_df = pd.read_csv(args.inputFileGamesStats)
games_stats_with_statistics_df = get_games_with_statistics(games_stats_df, False)
print(f"Encontrados {len(games_stats_with_statistics_df)} jogos")

all_games_df_list = []

for i, _game_df in games_stats_with_statistics_df.iterrows():
    if (i % 10 == 0):
        print(f"Processando jogo {i}/{len(games_stats_with_statistics_df)}")
    last_n_games_home_df = get_team_last_n_games_or_none(games_stats_df, _game_df['homeTeamId'], args.lastNGames)
    last_n_games_away_df = get_team_last_n_games_or_none(games_stats_df, _game_df['awayTeamId'], args.lastNGames)
    if (last_n_games_home_df is not None and last_n_games_away_df is not None):
        last_n_games_home_df = last_n_games_home_df.add_suffix('_home_x')
        last_n_games_away_df = last_n_games_away_df.add_suffix('_away_x')
        game_df = games_stats_with_statistics_df.iloc[[i]].add_suffix('_y').reset_index(drop=True)
        all_games_df_list.append(pd.concat([last_n_games_home_df, last_n_games_away_df, game_df], axis=1))

all_games_df = pd.concat(all_games_df_list, axis=0)
all_games_df.to_csv(Path(args.outputDir) / f'games_training_set_{args.lastNGames}.csv', index=False)