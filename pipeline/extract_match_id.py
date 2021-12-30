import json
import pandas as pd
import os

def extract_match_id(store, startTime, endTime, api_key, prefix, session):

    location = f'datahub/raw/match_id/{prefix}_match_id.json'

    if os.path.isfile(location):
        print('match ids already extracted...')
        return ''

    puuid_info = pd.read_json(store)['puuid'].to_list()
    match_id_entry = list()

    for puuid in puuid_info:
        match_id_url =  f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={startTime}&endTime={endTime}&type=ranked&start=0&count=100&api_key={api_key}"
        match_id_info = session.get(match_id_url)
        match_entry = {'puuid':puuid, 'match_id':match_id_info.json()}
        match_id_entry.append(match_entry)

    with open(location, 'w') as outfile:
        json.dump(match_id_entry, outfile)

    print('match ids extracted...')