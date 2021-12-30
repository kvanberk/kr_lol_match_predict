import json
import pandas as pd

def extract_summoner_spell_info(session, summoner_spell_url_link = "http://ddragon.leagueoflegends.com/cdn/11.24.1/data/en_US/summoner.json"):
    summoner_spell_information = session.get(summoner_spell_url_link).json()

    summoner_spell = pd.DataFrame.from_dict(summoner_spell_information['data'], orient='index')
    summoner_spell = summoner_spell[['id','key','description']].set_index('key').rename(columns={'id':'summoner_name', 'description': 'summoner_description'})

    with open('datahub/raw/resources/summoner_spell_list.json','w') as outfile:
        json.dump(summoner_spell.to_dict(), outfile)

    print('summoner spells extracted...')