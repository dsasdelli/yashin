import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from chromedriver_py import binary_path
from selenium.webdriver.support.wait import WebDriverWait 
from pathlib import Path

ID_BRASILEIRAO_SERIE_A = 325

URL = f"https://www.sofascore.com/pt/football/tournament/brazil/brasileirao-serie-a/{ID_BRASILEIRAO_SERIE_A}"

def create_driver():
    options = Options()
    options.headless = False
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--window-size=1920,1200")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    service_object = Service(binary_path)
    return webdriver.Chrome(service=service_object, options=options)

def get_json_page(url):
    driver.get(url)
    try:
        element = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, 'pre'))
        )
        return json.loads(element.text)    
    except TimeoutException:
        print("Timed out waiting for page to load")
        return None
    
def file_exists(filename):
    return Path(filename).is_file()
    
def dump_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_seasons(tournament_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/seasons")['seasons']

def get_rounds(tournament_id, season_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/rounds")['rounds']

def get_events(tournament_id, season_id, round_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/round/{round_id}")['events']

def get_event_details(event_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/event/{event_id}")['event']

def get_event_statistics(event_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/event/{event_id}/statistics")

def get_event_lineups(event_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/event/{event_id}/lineups")

def get_event_pregame_form(event_id):
    return get_json_page(f"https://www.sofascore.com/api/v1/event/{event_id}/pregame-form")

def del_keys(d, *keys):
    for key in keys:
        if key in d:
            del d[key]

driver = create_driver()

seasons = get_seasons(ID_BRASILEIRAO_SERIE_A)
for season in seasons:
    events = []
    if (file_exists(f'season_{season["year"]}.json')):
        print(f"Season {season['name']} already processed, skipping...")
        continue
    print(f"Processing season {season['name']}...")
    rounds = get_rounds(ID_BRASILEIRAO_SERIE_A, season['id'])
    for round in rounds:
        print(f"Processing round {round['round']}...")
        for event in get_events(ID_BRASILEIRAO_SERIE_A, season['id'], round['round']):
            event_details = get_event_details(event['id'])
            if (event_details['status']['type'] != 'finished'):
                continue
            event_statistics = get_event_statistics(event['id'])
            event_lineups = get_event_lineups(event['id'])
            event_pregame_form = get_event_pregame_form(event['id'])
            events.append({**event_details, **event_statistics, 'lineups': event_lineups, 'pregame_form': event_pregame_form})

    dump_json(f'season_{season["year"]}.json', events)

driver.quit()
