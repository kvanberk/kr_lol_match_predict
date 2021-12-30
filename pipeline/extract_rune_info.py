import json
import pandas as pd

def extract_rune_info(session, rune_url_link = "http://ddragon.leagueoflegends.com/cdn/11.24.1/data/en_US/runesReforged.json"):
    rune_information = session.get(rune_url_link).json()
    rune_dictionary = list()

    for runes in rune_information:
        for rune in runes['slots']:
            for entry in rune['runes']:
                id = entry['id']
                key = entry['key']
                shortDesc = entry['shortDesc']

                rune_dictionary.append({'id': id,
                                        'key': key,
                                        'shortDesc': shortDesc})

    runes_df = pd.DataFrame(rune_dictionary).set_index('id').rename(columns={'key': 'rune_name', 'shortDesc': 'rune_desc'})

    with open('datahub/raw/resources/rune_list.json','w') as outfile:
        json.dump(runes_df.to_dict(), outfile)

    print('runes extracted...')