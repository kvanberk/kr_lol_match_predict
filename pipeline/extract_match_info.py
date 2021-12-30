import json
import pandas as pd
import os

def extract_match_info(store, api_key, prefix, session):

    location = f'datahub/raw/match_info/{prefix}_match_info.json'

    if os.path.isfile(location):
        print('match info already extracted...')
        return ''

    # pull in dictionary countaining valid ranked queue type
    queue_dictionary_directory = 'datahub/raw/resources/queue_id.json'
    with open(queue_dictionary_directory) as f:
        queue_dictionary = json.load(f)['queue_name']

    match_info_entry = list()
    match_ids = pd.read_json(store).explode('match_id')['match_id'].dropna().drop_duplicates().reset_index(drop=True).to_list()

    for match in match_ids:
        match_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match}?api_key={api_key}"
        match_info = session.get(match_url).json()

        # skips any games which are not ranked solo
        if queue_dictionary[str(match_info['info']['queueId'])] != '5v5 Ranked Solo games':
            continue

        participants = match_info['info']['participants']

        # needs to be looped due to double-triple nested dictionaries in cells
        for participant in participants:
            perks = participant['perks']
            stat_perks = perks['statPerks']
            main_rune_perks = perks['styles'][0]['selections']
            sub_rune_perks = perks['styles'][1]['selections']

            details = {'summoner_name': participant['summonerName'],
                       'summoner_id': participant['summonerId'],
                       'champion_name': participant['championName'],
                       'champion_id': participant['championId'],
                       'team_id': participant['teamId'],
                       'match_id': match,
                       'patch': match_info['info']['gameVersion'],
                       'position': participant['teamPosition'],
                       'summoner_spell_1': participant['summoner1Id'],
                       'summoner_spell_2': participant['summoner2Id'],
                       'defense_perk': stat_perks['defense'],
                       'flex_perk': stat_perks['flex'],
                       'offense_perk': stat_perks['offense'],
                       'main_perk_1': main_rune_perks[0]['perk'],
                       'main_perk_2': main_rune_perks[1]['perk'],
                       'main_perk_3': main_rune_perks[2]['perk'],
                       'main_perk_4': main_rune_perks[3]['perk'],
                       'sub_perk_1': sub_rune_perks[0]['perk'],
                       'sub_perk_2': sub_rune_perks[1]['perk'],
                       'match_result': participant['win']
                       }

            match_info_entry.append(details)

    with open(location, 'w') as outfile:
        json.dump(match_info_entry, outfile)

    print('match info extracted...')