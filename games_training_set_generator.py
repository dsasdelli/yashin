import argparse
from pathlib import Path
import pandas as pd

from helper import get_players_last_n_games_or_none, get_starting_players_ids_by_side, get_games_with_statistics

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--inputFilePlayersGamesStats', help='input file players-games', default='games-players-processed/players_games_stats.csv')
parser.add_argument('-g', '--inputFileGamesStats', help='input file games', default='games-players-processed/games_stats.csv')
parser.add_argument('-o', '--outputDir', help='output directory', default='games-players-processed')
parser.add_argument('-l', '--lastNGames', type=int, help='last n games to consider', default=5)

args = parser.parse_args()

games_stats_df = pd.read_csv(args.inputFileGamesStats)
players_games_stats_df = pd.read_csv(args.inputFilePlayersGamesStats)

games_stats_with_statistics_df = get_games_with_statistics(games_stats_df)
print(f"Encontrados {len(games_stats_with_statistics_df)} jogos")

all_games_df_list = []

for i, _game_df in games_stats_with_statistics_df.iterrows():
    starting_players_ids_home = get_starting_players_ids_by_side(players_games_stats_df, _game_df['gameId'], 'home')
    starting_players_ids_away = get_starting_players_ids_by_side(players_games_stats_df, _game_df['gameId'], 'away')
    if (i % 10 == 0):
        print(f"Processando jogo {i}/{len(games_stats_with_statistics_df)}")
    players_last_n_games_home_df = get_players_last_n_games_or_none(players_games_stats_df, starting_players_ids_home, last_n=args.lastNGames, start_timestamp=_game_df['startTimestamp'])
    players_last_n_games_away_df = get_players_last_n_games_or_none(players_games_stats_df, starting_players_ids_away, last_n=args.lastNGames, start_timestamp=_game_df['startTimestamp'])
    if (players_last_n_games_home_df is not None and players_last_n_games_away_df is not None):
        players_last_n_games_home_df = players_last_n_games_home_df.add_suffix('_home_x')
        players_last_n_games_away_df = players_last_n_games_away_df.add_suffix('_away_x')
        game_df = games_stats_with_statistics_df.iloc[[i]].add_suffix('_y').reset_index(drop=True)
        all_games_df_list.append(pd.concat([players_last_n_games_home_df, players_last_n_games_away_df, game_df], axis=1))

all_games_df = pd.concat(all_games_df_list, axis=0).reset_index(drop=True)
all_games_df.to_csv(Path(args.outputDir) / f'players_games_training_set_{args.lastNGames}.csv', index=False)