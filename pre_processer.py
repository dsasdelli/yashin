import argparse
from itertools import chain
import json
import dictutils as du
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputDir', help='input directory', default='seasons-raw', required=True)
parser.add_argument('-o', '--outputDir', help='output directory', default='games-flattened', required=True)

args = parser.parse_args()

def filter(obj):
    return du.dict_key_filter(obj, [
        'id'
        'season.year',
        'roundInfo',
        'status.type',
        'venue.[id,venueCoordinates,name,city,capacity]',
        'referee.[id,name,country.name]',
        'homeTeam.[id,name,manager.[id,name,country.name],foundationDateTimestamp]',
        'awayTeam.[id,name,manager.[id,name,country.name],foundationDateTimestamp]',
        'homeScore.[normalTime,period1,period2]',
        'awayScore.[normalTime,period1,period2]',
        'hasEventPlayerStatistics',
        'hasEventPlayerHeatMap',
        'startTimestamp',
        'currentPeriodStartTimestamp',
        'lineups.home.players.[' 
            +'player.[id,name,height,country.name,dateOfBirthTimestamp,proposedMarketValueRaw],'
            +'teamId,position,shirtNumber,substitute,statistics'
        +']',
        'lineups.away.players.[' 
            +'player.[id,name,height,country.name,dateOfBirthTimestamp,proposedMarketValueRaw],'
            +'teamId,position,shirtNumber,substitute,statistics'
        +']'
    ]),

def flatten(obj):
    obj = list(chain.from_iterable(obj))
    return du.flatten(obj)

dir_path = Path(args.inputDir)
for file_path in dir_path.iterdir():
    if file_path.is_file():
        print(f"Processing file {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        obj_processed = flatten(filter(obj))
        output_dir = Path(args.outputDir)
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / file_path.name
        with open(file_path, 'w', encoding='utf-8') as f:
             json.dump(obj_processed, f, ensure_ascii=False, indent=4)



