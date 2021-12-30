import json
import pandas as pd
import os

def extract_participant_info(store, api_key, prefix, session):

    location = f'datahub/raw/summoner_info/participants/{prefix}_participant_info.json'

    if os.path.isfile(location):
        print('participant info already extracted...')
        return ''

    participants = pd.read_json(store)['summoner_id'].drop_duplicates().to_list()

    participant_info_entry = list()

    for participant in participants:
        participant_url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{participant}?api_key={api_key}"
        participant_info = session.get(participant_url).json()

        # since each ranked participant  can have many related league stats, we need to pull summoner rift queue information
        for info in participant_info:
            if info['queueType'] == "RANKED_SOLO_5x5":
                participant_info = info
            else:
                participant_info =[]

        # incase of rare event that summonerId no longer exists (e.g. bans, deactivation, temporary accounts)
        if len(participant_info) == 0:
            continue

        details = {'summoner_id': participant_info['summonerId'],
                   'league_points': participant_info['leaguePoints'],
                   'wins': participant_info['wins'],
                   'losses': participant_info['losses'],
                   'hotstreak':participant_info['hotStreak']
                   }

        participant_info_entry.append(details)

    with open(location, 'w') as outfile:
        json.dump(participant_info_entry, outfile)

    print('participant info extracted...')

