import json
import os

def extract_challengers(api_key, prefix, session):
    player_list = session.get(f'https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}')
    storage_location = os.path.join("datahub/raw/challenger_list",f"{prefix}_challenger_list.json")

    with open(storage_location, 'w') as outfile:
        json.dump(player_list.json()['entries'], outfile)

    print('challengers extracted...')