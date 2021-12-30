import os
import glob
import pandas as pd
import json

def extract_champion_stat_info():
    files = glob.glob("datahub/raw/champion_win_rates/*.txt")
    champion_stats = []

    for file in files:
        with open(file) as f:
            lines = f.readlines()
        role = os.path.basename(file).split('.')[0]

        for i, line in enumerate(lines):
            if i == 0:
                entry = []
            if i%4 ==0:
                entry.append(role)

            entry.append(line)

            if (i+1)%4 == 0 and i != 0:
                champion_stats.append(entry)
                entry = []
                continue

    dataframe = pd.DataFrame(champion_stats)[[0,2,4]]
    dataframe.columns = ['role','champion','win_rate']

    # parsing out special characters
    dataframe['champion'] = dataframe['champion'].apply(lambda x: x.replace("\n",""))
    dataframe['win_rate'] = dataframe['win_rate'].apply(lambda x: x.split("%\t",1)[0]).astype(float)/100

    with open('datahub/raw/champion_win_rates/champion_win_rates.json', 'w') as outfile:
        json.dump(dataframe.to_dict(), outfile)

    print('champion stat info processing complete...')