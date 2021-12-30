# packages
import os, requests
from datetime import datetime, timedelta, date
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# individual processes which api request to riot services
from pipeline.extract_summoner_spell_info import extract_summoner_spell_info
from pipeline.extract_rune_info import extract_rune_info
from pipeline.extract_queue_id import extract_queue_id
from pipeline.extract_challengers import extract_challengers
from pipeline.extract_summoner_info import extract_summoner_info
from pipeline.extract_match_id import extract_match_id
from pipeline.extract_match_info import extract_match_info
from pipeline.extract_participant_info import extract_participant_info
from pipeline.extract_champion_mastery_info import extract_champion_mastery_info
from pipeline.extract_champion_stat_info import extract_champion_stat_info

# intialise api service
def get_api_key():
    with open(parent_directory + "/restricted/api_key") as f:
        api_key = f.read()

    return api_key

# backoff function to avoid overloading riot api service
def requests_retry(retries=5,backoff_factor=0.1):
    session = requests.Session()
    retry=Retry(total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor
                )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# generate location of output files
def generate_directory(parent_directory, sub_directory, prefix, file):
    return f"{parent_directory}\{sub_directory}\{prefix}_{file}"

# git pull request friendly directory
parent_directory = os.getcwd()

# script parameters
session = requests_retry()

# api key initialisation
api_key = get_api_key()

# logic to create time parameters with api and prefix naming convention
days = 1 # controls time parameters. by default this is set to 1 so scheduling fetches the previous day's data
prefix = datetime.now() - timedelta(days=days)
prefix = prefix.strftime("%Y_%m_%d")
date_end = date.today() - timedelta(days=days)
date_end = datetime(date_end.year, date_end.month, date_end.day)
date_start = date_end - timedelta(days=days)
epoch_end = int(date_end.timestamp())
epoch_start = int(date_start.timestamp())

# generate directory locations to store and pull data in any foreign environment
sub_dir1 = generate_directory(parent_directory, 'datahub/raw/challenger_list', prefix, 'challenger_list.json')
sub_dir2 = generate_directory(parent_directory, 'datahub/raw/summoner_info/challenger', prefix, 'challenger_info.json')
sub_dir3 = generate_directory(parent_directory, 'datahub/raw/match_id', prefix , 'match_id.json')
sub_dir4 = generate_directory(parent_directory, 'datahub/raw/match_info', prefix, 'match_info.json')

# calling all pipelines scripts to execute chained api calls
extract_summoner_spell_info(session=session)
extract_rune_info(session=session)
extract_queue_id(session=session)
extract_challengers(api_key=api_key, prefix=prefix, session=session)
extract_summoner_info(store=sub_dir1,api_key=api_key, prefix=prefix, session=session)
extract_match_id(store=sub_dir2, startTime=epoch_start, endTime=epoch_end, api_key=api_key, prefix=prefix, session=session)
extract_match_info(store=sub_dir3, api_key=api_key, prefix=prefix, session=session)
extract_participant_info(store=sub_dir4, api_key=api_key, prefix=prefix, session=session)
extract_champion_mastery_info(store=sub_dir4, api_key=api_key, prefix=prefix, session=session)
extract_champion_stat_info() # c&p from https://oce.op.gg/champion/statistics for now, as api doesn't exist from riot and webscapping with requests is clouflare blocking requests from 3rd party sites
