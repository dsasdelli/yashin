import argparse
from pathlib import Path
import json
import pandas as pd
from util import create_dir

def genStatisticalItems(game, period, groupName) -> None | list:
    _game_statistics = dict() 
    if 'statistics' not in game:
        return None
    for si in [g for g in [p for p in game['statistics'] if p['period'] == period][0]['groups'] if g['groupName'] == groupName][0]['statisticsItems']:
        _game_statistics[f'home{si["key"].capitalize()}'] = si['homeValue']
        _game_statistics[f'away{si["key"].capitalize()}'] = si['awayValue']
    return _game_statistics

def getPlayerGameStats(game) -> None | list:
    _players_games_stats = []
    for side in ['home', 'away']:
        if 'home' not in game['lineups'] or 'away' not in game['lineups']:
            return None 
        for player in game['lineups'][side]['players']:
                if 'statistics' not in player:
                    return None
                player_stat = {
                    'playerId': player['player']['id'],
                    'playerName': player['player']['name'],
                    'dateOfBirthTimestamp': player['player']['dateOfBirthTimestamp'] if 'dateOfBirthTimestamp' in player['player'] else None,
                    'height': player['player']['height'] if 'height' in player['player'] else None,
                    'country': player['player']['country']['name'] if 'country' in player['player'] and 'name' in player['player']['country'] else None,
                    'teamId': player['teamId'],
                    'position': player['position'],
                    'substitute': player['substitute'],
                    **{key:value for (key, value) in player['statistics'].items() if key != 'statisticsType'},
                    'side': side
                }
                _players_games_stats.append({**player_stat})
    return _players_games_stats

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputDir', help='input directory', default='games-raw')
parser.add_argument('-o', '--outputDir', help='output directory', default='games-players-processed')

args = parser.parse_args()

game_stats = []
players_games_stats = []

dir_path = Path(args.inputDir)
for file_path in dir_path.iterdir():
    if file_path.is_file():
        print(f"Processing file {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            games = json.load(f)
            i = 0
            for game in games:
                if (i % 100 == 0):
                    print(f"Processed {i} games...")
                i += 1
                base_game_stat = {
                    'gameId': game['id'],
                    'startTimestamp': game['startTimestamp']
                }
                _players_games_stats = getPlayerGameStats(game)
                _game_stats = genStatisticalItems(game, 'ALL', 'Match overview')
                if not _game_stats:
                    print(f"Warning: Game {game['id']} does not have statistics, skipping...")
                    continue
                if _players_games_stats:
                    players_games_stats.extend([{**_p, **base_game_stat} for _p in _players_games_stats])
                else:
                    continue
                game_stat = {
                    **base_game_stat,
                    'seasonYear': game['season']['year'],
                    'round': game['roundInfo']['round'],
                    'statusType': game['status']['type'],
                    # Home team:
                    'homeTeamId': game['homeTeam']['id'],
                    'homeTeamName': game['homeTeam']['name'],
                    'homeTeamFoundationDateTimestamp': game['homeTeam']['foundationDateTimestamp'],
                    # Home team score:
                    'homeScoreNormalTime': game['homeScore']['normaltime'],
                    'homeScorePeriod1': game['homeScore']['period1'] if 'period1' in game['homeScore'] else None,
                    'homeScorePeriod2': game['homeScore']['period2'] if 'period2' in game['homeScore'] else None,
                    # Away team:
                    'awayTeamId': game['awayTeam']['id'],
                    'awayTeamName': game['awayTeam']['name'],
                    'awayTeamFoundationDateTimestamp': game['awayTeam']['foundationDateTimestamp'],
                    # Away team score:
                    'awayScoreNormalTime': game['awayScore']['normaltime'],
                    'awayScorePeriod1': game['awayScore']['period1'] if 'period1' in game['awayScore'] else None,
                    'awayScorePeriod2': game['awayScore']['period2'] if 'period2' in game['awayScore'] else None,
                    # Referee:
                    'refereeId': game['referee']['id'] if 'referee' in game and 'id' in game['referee'] else None,
                    'refereeName': game['referee']['name'] if 'referee' in game and 'name' in game['referee'] else None,
                    # Game stats:
                    **_game_stats
                }
                game_stats.append(game_stat)


create_dir(args.outputDir)

pd.DataFrame(game_stats).to_csv(Path(args.outputDir) / 'games_stats.csv', index=False)
pd.DataFrame(players_games_stats).to_csv(Path(args.outputDir) / 'players_games_stats.csv', index=False)

                