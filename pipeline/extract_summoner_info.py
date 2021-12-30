import json
import pandas as pd
import os

def extract_summoner_info(store, api_key, prefix, session):

    location = f'datahub/raw/summoner_info/challenger/{prefix}_challenger_info.json'

    if os.path.isfile(location):
        print('summoner info already extracted...')
        return ''

    summoner_info = pd.read_json(store)['summonerId'].to_list()
    summoner_entry = list()

    for summonerId in summoner_info:
        summoner_info_url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}?api_key={api_key}"
        summoner_info = session.get(summoner_info_url)
        summoner_entry.append(summoner_info.json())

    with open(location, 'w') as outfile:
        json.dump(summoner_entry, outfile)

    print('summoner info extracted...')
