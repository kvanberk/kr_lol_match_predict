import pandas as pd

# creates individual dataframes with prefix
def sub_dataframe_create(team_id, position):
    sub_df = quality_df[(quality_df.team_id == team_id) & (quality_df.position == position)]
    sub_df = sub_df.drop(columns=['team_id', 'position'])
    prefix = f'{team_id}_{position}_'
    sub_df = sub_df.add_prefix(prefix).rename(columns = {f'{prefix}match_id':'match_id'}).set_index('match_id')
    return sub_df

df = pd.read_json(r'datahub\validated\match_dataset.json')

# removing data quality issues caused by api service
quality_features = ['summoner_name', 'summoner_id', 'champion_name', 'champion_id',
       'team_id', 'match_id', 'patch', 'position', 'summoner_spell_1',
       'summoner_spell_2', 'defense_perk', 'flex_perk', 'offense_perk',
       'main_perk_1', 'main_perk_2', 'main_perk_3', 'main_perk_4',
       'sub_perk_1', 'sub_perk_2', 'match_result', 'champion_win_rate']

quality_df = df[quality_features].drop_duplicates()

# getting the first instance summoner data if duplicates occur because of api service issues
quality_df = quality_df.join(df[['championPoints','league_points','wins','losses','hotstreak']])

# engineering features
quality_df['championPoints'] = quality_df['championPoints'].fillna(0)
quality_df['win_rate'] = quality_df['wins']/(quality_df['wins']+quality_df['losses'])
quality_df['league_points'] = quality_df['league_points']/quality_df['league_points'].max() #minmax scaling as the data is linear and xmin is always known at 0
quality_df['championPoints'] = quality_df['championPoints']/quality_df['championPoints'].max() #minmax scaling as the data is linear and xmin is always known at 0
quality_df['champion_win_rate'] = quality_df['champion_win_rate'].fillna(0.5) #default any odd champion-role combinations to 50% (coin-flip)

# get match ids which have users with no winrates.
match_issues_win_rates = quality_df[quality_df['win_rate'].isna()]['match_id']
match_issues_position  = quality_df[quality_df['position']=='']['match_id']

#filter these matches out
quality_df = quality_df[~quality_df['match_id'].isin(match_issues_win_rates)]
quality_df = quality_df[~quality_df['match_id'].isin(match_issues_position)]

# selecting features for preliminary analysis
features = ['champion_name','team_id','position', 'summoner_spell_1','summoner_spell_2',
             'defense_perk', 'flex_perk', 'offense_perk','main_perk_1', 'main_perk_2', 'main_perk_3',
             'main_perk_4','sub_perk_1', 'sub_perk_2', 'match_result', 'championPoints','league_points',
            'win_rate', 'hotstreak', 'champion_win_rate','match_id']

quality_df = quality_df[features]

#converting datasets which are misclassified
quality_df['hotstreak'] = quality_df['hotstreak'].astype('int')

# creating individual dataframes to concat later
blue_top_df = sub_dataframe_create('blue','TOP')
blue_jungle_df = sub_dataframe_create('blue','JUNGLE')
blue_middle_df = sub_dataframe_create('blue','MIDDLE')
blue_bottom_df = sub_dataframe_create('blue','BOTTOM')
blue_utility_df = sub_dataframe_create('blue','UTILITY')

red_top_df = sub_dataframe_create('red','TOP')
red_jungle_df = sub_dataframe_create('red','JUNGLE')
red_middle_df = sub_dataframe_create('red','MIDDLE')
red_bottom_df = sub_dataframe_create('red','BOTTOM')
red_utility_df = sub_dataframe_create('red','UTILITY')

# concating the dataframes together
dataset = pd.concat([blue_top_df,
                    blue_jungle_df,
                    blue_middle_df,
                    blue_bottom_df,
                    blue_utility_df,
                    red_top_df,
                    red_jungle_df,
                    red_middle_df,
                    red_bottom_df,
                    red_utility_df
                    ], axis=1)

# unifying match results into a single field as target variable, whislt dropping match results from other columns
dataset['match_team_win'] = dataset['blue_UTILITY_match_result'].astype('int')
dataset = dataset.drop(columns = ['blue_TOP_match_result',
                                  'blue_BOTTOM_match_result',
                                  'blue_JUNGLE_match_result',
                                  'blue_UTILITY_match_result',
                                  'blue_MIDDLE_match_result',
                                  'red_TOP_match_result',
                                  'red_BOTTOM_match_result',
                                  'red_JUNGLE_match_result',
                                  'red_UTILITY_match_result',
                                  'red_MIDDLE_match_result'],
                       axis=1)
# formats dataset for datascience use
feature_dataset = pd.get_dummies(dataset)
feature_dataset.to_csv('datahub/access/match_dataset.csv')