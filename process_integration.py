import pandas as pd
import json
import os
from datetime import datetime, timedelta
import re

def generate_directory(parent_directory, sub_dir):
    location = os.path.join(parent_directory, sub_dir)
    return location

def dict_load(parent_directory, sub_dir):
    location = generate_directory(parent_directory, sub_dir)
    with open(location) as f:
        return json.load(f)

# time functions
prefix = datetime.now() - timedelta(days=1)
prefix = prefix.strftime("%Y_%m_%d")

# git pull request friendly directory
parent_directory = os.getcwd()
store_directory = os.path.join(parent_directory, 'datahub/raw/')
perk_list_dir = generate_directory(store_directory,"resources/perk_list.json")
rune_list_dir = generate_directory(store_directory,"resources/rune_list.json")
summoner_spell_list_dir = generate_directory(store_directory,"resources/summoner_spell_list.json")
match_info_dir = generate_directory(store_directory, f"match_info/{prefix}_match_info.json")
champion_mastery_dir = generate_directory(store_directory, f"champion_mastery/{prefix}_mastery_info.json")
participant_info_dir = generate_directory(store_directory, f"summoner_info/participants/{prefix}_participant_info.json")
champion_win_rate_dir = generate_directory(store_directory,"champion_win_rates/champion_win_rates.json")

validated_dir = generate_directory(parent_directory, "datahub/validated/match_dataset.json")

# dictionary lookups to replace ids with text
perk_list = dict_load(store_directory, perk_list_dir)
rune_list = dict_load(store_directory, rune_list_dir)
summoner_spell_list = dict_load(store_directory, summoner_spell_list_dir)

# importing relevant datasets to merge
match_info = pd.read_json(match_info_dir)
champion_mastery = pd.read_json(champion_mastery_dir)
participant_info = pd.read_json(participant_info_dir)
champion_win_rate = pd.read_json(champion_win_rate_dir)

# merging datasets
dataframe = match_info.merge(champion_mastery, how = 'left', left_on = ['summoner_id','champion_id'], right_on = ['summoner_id', 'champion_id'])
dataframe = dataframe.merge(participant_info, how = 'left', on = 'summoner_id')

# formatting datasets with values in a presentable form
dataframe['team_id'] = dataframe['team_id'].apply(lambda x: 'blue' if x == 100 else 'red')
summoner_spell_features = ['summoner_spell_1','summoner_spell_2']
rune_features = ['main_perk_1','main_perk_2','main_perk_3','main_perk_4','sub_perk_1','sub_perk_2']
perk_features = ['defense_perk', 'flex_perk', 'offense_perk']

for spell in summoner_spell_features:
    dataframe[spell] = dataframe[spell].apply(lambda x: summoner_spell_list['summoner_name'][str(x)])

for rune in rune_features:
    dataframe[rune] = dataframe[rune].apply(lambda x: rune_list['rune_name'][str(x)])

for perk in perk_features:
    dataframe[perk] = dataframe[perk].apply(lambda x: perk_list[str(x)])

role_dict = {'adc':'BOTTOM','jungle':'JUNGLE', 'mid': 'MIDDLE','top':'TOP','support':'UTILITY'}

#creating joinable field to champion win rates
dataframe['champion_name_format'] = dataframe['champion_name'].str.lower()

#cleaning champion win rate df to make it joinable
champion_win_rate['champion'] = champion_win_rate['champion'].apply(lambda x: re.sub('[^\w\s]','',x).replace(' ','').lower())
champion_win_rate['role'] = champion_win_rate['role'].apply(lambda x: role_dict[x])
champion_win_rate = champion_win_rate.rename(columns = {'win_rate':'champion_win_rate'})

dataframe = dataframe.merge(champion_win_rate, how = 'left', left_on = ['champion_name_format', 'position'], right_on = ['champion', 'role'])
dataframe = dataframe.drop(['champion','role','champion_name_format'], axis=1)

# simulating database in hdfs
if os.path.isfile(validated_dir):
    validated = pd.read_json(validated_dir)
    validated = pd.concat([validated, dataframe], ignore_index=True).drop_duplicates().reset_index(drop=True)
    validated.to_json(validated_dir)
else:
    dataframe.to_json(validated_dir)