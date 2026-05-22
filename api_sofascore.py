import argparse
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from chromedriver_py import binary_path
from selenium.webdriver.support.wait import WebDriverWait 
import time
from util import create_dir, file_exists, dump_json
from modelo import ANOS, COMPETICOES

def create_driver():
    options = Options()
    options.headless = False
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--window-size=1920,1200")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    service_object = Service(binary_path)
    return webdriver.Chrome(service=service_object, options=options)

def get_json_page(url, wait_time=3):
    time.sleep(wait_time)
    driver.get(url)
    try:
        element = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'pre'))
        )
        return json.loads(element.text)    
    except TimeoutException:
        print("Timed out waiting for page to load")
        return None
    
def keep_numbers_only(string):
    return ''.join(filter(str.isdigit, string))

def get_seasons(tournament_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/seasons")['seasons']

def get_rounds(tournament_id, season_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/rounds")['rounds']

def get_events(tournament_id, season_id, round_id, round_slug):
    if (round_slug is None):
        return get_json_page(f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/round/{round_id}")['events']
    else:
        return get_json_page(f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/round/{round_id}/slug/{round_slug}")['events']

def get_event_details(event_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/event/{event_id}")['event']

def get_event_statistics(event_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/event/{event_id}/statistics")

def get_event_lineups(event_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/event/{event_id}/lineups")

def get_event_pregame_form(event_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/event/{event_id}/pregame-form")

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--anoInicio', type=int, help='Ano de início', choices=ANOS, required=False, default=ANOS[0])
parser.add_argument('-f', '--anoFim', type=int, help='Ano de fim', choices=ANOS, required=False, default=ANOS[-1])
parser.add_argument('-o', '--outputDir', help='output directory', required=False, default='games-raw')
parser.add_argument('-c', '--competicao', help='Competição', choices=list(COMPETICOES.keys()), required=True)

args = parser.parse_args()

driver = create_driver()

create_dir(args.outputDir)

seasons = get_seasons(COMPETICOES[args.competicao]["ID"])
for season in seasons:
    events = []
    if (file_exists(args.outputDir, f'{args.competicao}_{season["year"]}.json')):
        print(f"Season {season['year']} already processed, skipping...")
        continue
    if (int(keep_numbers_only(season['year'])) < args.anoInicio or int(keep_numbers_only(season['year'])) > args.anoFim):
        print(f"Season {season['year']} is out of range, skipping...")
        continue
    print(f"Processing season {season['year']}...")
    rounds = get_rounds(COMPETICOES[args.competicao]["ID"], season['id'])
    for round in rounds:
        print(f"Processing round {round['round']}...")
        for event in get_events(COMPETICOES[args.competicao]["ID"], season['id'], round['round'], round['slug'] if 'slug' in round else None):
            event_details = get_event_details(event['id'])
            if (event_details['status']['type'] != 'finished'):
                continue
            event_statistics = get_event_statistics(event['id'])
            event_lineups = get_event_lineups(event['id'])
            event_pregame_form = get_event_pregame_form(event['id'])
            events.append({**event_details, **event_statistics, 'lineups': event_lineups, 'pregame_form': event_pregame_form})

    dump_json(args.outputDir, f'{args.competicao}_{season["year"]}.json', events)

driver.quit()
