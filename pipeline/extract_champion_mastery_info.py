import json
import pandas as pd
import os

def extract_champion_mastery_info(store, api_key, prefix, session):

    storage_location = f"datahub/raw/champion_mastery/{prefix}_mastery_info.json"
    if os.path.isfile(storage_location):
        print('mastery info already extracted...')
        return ''

    participants = pd.read_json(store)['summoner_id'].drop_duplicates().to_list()

    mastery_info_entry = list()

    for participant in participants:
        participant_url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{participant}?api_key={api_key}"
        masteries = session.get(participant_url).json()
        mastery_df = pd.DataFrame(masteries)[['summonerId','championPoints','championId']].rename(columns = {'summonerId':'summoner_id','championId':'champion_id'})
        mastery_info_entry += mastery_df.to_dict(orient = 'records')

    with open(storage_location, 'w') as outfile:
        json.dump(mastery_info_entry, outfile)

    print('mastery info extracted...')