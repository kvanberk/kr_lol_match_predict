# kr_lol_match_predict
Python project that utilises Korean challenger match information to predict match outcomes based on draft strategies 

Repo includes the following;
1. ETLs that extract various summoner data via API requests and creates a master dataset of match information
2. Analyses the match information for various insights
3. Creates a Logistic Regression classification model to predict the outcome of matches based on draft strategy information
4. Plotly-Dash web-application front end to display various information
5. Pseudo Datahub directory with the intention this can be stored in a database file structure like hdfs
