import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import warnings

# ignoring warning markers
warnings.filterwarnings("ignore")

# initialising application
app = dash.Dash(__name__)

# pulling in data from the pseudo datahub
df = pd.read_json('datahub/validated/match_dataset.json')

# creating sub dataset for graph1 and graph2 visualising
df['match_result'] = df['match_result'].apply(lambda x: 'Win' if x is True else 'Loss')
df1 = df[['champion_name','match_result','summoner_name','position']]
df1 = df1.rename(columns = {'match_result': 'Match Outcome'})

# creating dash table sub dataset
dash_table_features = ['summoner_name','champion_name','position', 'match_result']
df_table = df[dash_table_features]

# cleaning results for table visualisation
df_table['position'] = df_table['position'].apply(lambda x: x.title())
df_table['value'] = 1

# creating pivot table to calculate statistics
df_table = pd.pivot_table(df_table, values = 'value', index=['summoner_name','champion_name','position'], columns = ['match_result'], aggfunc = np.sum, fill_value = 0).reset_index()
df_table['total'] = df_table['Win'] + df_table['Loss']
df_table['win_rate'] = round(df_table['Win']/df_table['total']*100,2)

# limiting dataset for visualisation
df_table = df_table.reset_index()[['summoner_name','champion_name','position','total','Win','Loss','win_rate']]

# formatting table names
df_table = df_table.rename(columns = {'summoner_name': 'Summoner Name',
                                      'champion_name': 'Champion Name',
                                      'position': 'Role',
                                      'Win': 'Wins',
                                      'Loss': 'Losses',
                                      'total': 'Games Played',
                                      'win_rate': 'Win Rate (%)'})

# note the above could be created in a separate etl, however, for this exercise, giving the small scale of it, etls are down within the visualisation script

# dropdown filter component
dropdown_summoner = dcc.Dropdown(
    id='dropdown_summoner',
    options=[{'label':x , 'value': x}
               for x in df['summoner_name'].drop_duplicates()],
    placeholder='Select a Summoner ',
    multi=False
)

# radioitem filter component
radio_match = dcc.RadioItems(
    id='radio_match',
    options=[
        {'label': 'All', 'value': 'All'},
        {'label': 'Win', 'value': 'Win'},
        {'label': 'Loss', 'value': 'Loss'}
    ],
    value = 'All',
    labelStyle={'display': 'inline-block', 'margin-right': 10},
    inputStyle={"margin-right": "6px"}

)

# making sub html div for filters to be aggregated together
filters = html.Div(
            [
                dbc.Label('Summoners'),
                dropdown_summoner,
                html.Br(),
                dbc.Label('Match Outcome'),
                radio_match
            ]
        )

# styling the sidebar
sidebar_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# sidebar creation
sidebar = html.Div(
    [
        html.H6("Korean Challengers",
                className="display-name",
                style={'font-size':'40px'}),
        html.Hr(),
        html.P(
            "Summoner Insights", className="lead"
        ),
        html.Br(),
        dbc.Col(filters),
    ],
    style=sidebar_style
)

# creating dash table visual
dash_table = dash_table.DataTable(
    id='info_table',
    columns = [{'name':i, 'id':i} for i in df_table],
    data=df_table.to_dict('records'),
    page_size = 100,
    fixed_rows={'headers':True},
    style_table={'width':'100%', 'height':'250px'},
    export_format='csv',
    export_headers='display',
    sort_action="native",
    style_cell_conditional=[
        {'if': {'column_id': 'Summoner Name'},
         'width': '30%'},
        {'if': {'column_id': 'Champion Name'},
         'width': '10%'},
        {'if': {'column_id': 'Role'},
         'width': '10%'},
        {'if': {'column_id': 'Wins'},
         'width': '10%'},
        {'if': {'column_id': 'Losses'},
         'width': '10%'},
        {'if': {'column_id': 'Win Rate (%)'},
         'width': '10%'},
        {'if': {'column_id': 'Games Played'},
         'width': '10%'}
    ],
)

# creating html structure in dash
app.layout = html.Div(
    [
        html.Div([sidebar]),
        dbc.Row(html.Br()),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id = 'graph1',
                              figure={}),
                    md = 4,
                    width={'offset':3}
                ),
                dbc.Col(
                    dcc.Graph(id = 'graph2',
                              figure={}),
                    md = 4
                )
            ]
        ),
        dbc.Row([
            dbc.Col(
                html.Div(
                    dbc.Label('Details',
                              style={'font-family':'Arial',
                                     'font-size':'17px'})
                    ),
                width={'offset':3},
            )
        ]),
        dbc.Row([
            dbc.Col(
                dash_table,
                md = 8,
                width={'offset':3}
            )
        ])
    ]
)

# creating call back functions to allow user interaction
# callback for graph 1
@app.callback(
    Output('graph1','figure'),
    [Input('dropdown_summoner', 'value'),
     Input('radio_match', 'value')]
)

# function to allow for dynamic interaction
def generate_graph1(x,y):
    graph1_df = df1
    color_discrete_sequence = []

    if y != 'All':
        graph1_df = graph1_df[graph1_df['Match Outcome'] == y]

    if x is not None and x != '':
        graph1_df = graph1_df[graph1_df.summoner_name == x]

    graph1_df = graph1_df.groupby(['champion_name','Match Outcome']).count().sort_values('position').reset_index()

    graph1 = px.bar(
        graph1_df,
        x='summoner_name',
        y='champion_name',
        color='Match Outcome',
        orientation='h',
        title='Champion Performance',
        labels={'champion_name': 'Champion Name',
                'summoner_name': 'No. of Matches'
                },
        color_discrete_map ={'Loss': 'Red', 'Win': 'Green'}
    )

    return graph1

# call back for graph2
@app.callback(
    Output('graph2','figure'),
    [Input('dropdown_summoner', 'value'),
     Input('radio_match', 'value')]
)

# function to allow for dynamic interaction
def generate_graph2(x,y):
    graph2_df = df1[df1.position != '']
    color_discrete_sequence = []

    if y != 'All':
        graph2_df = graph2_df[graph2_df['Match Outcome'] == y]

    if x is not None and x != '':
        graph2_df = graph2_df[graph2_df.summoner_name == x]

    graph2_df = graph2_df.groupby(['position','Match Outcome']).count().sort_values('summoner_name').reset_index()

    graph2 = px.bar(
        graph2_df,
        x='summoner_name',
        y='position',
        color='Match Outcome',
        orientation='h',
        title='Position Performance',
        labels={'position': 'Team Position',
                'summoner_name': 'No. of Matches'
                },
        color_discrete_map ={'Loss': 'Red', 'Win': 'Green'}
    )

    return graph2

# callback for dash table
@app.callback(
    Output('info_table','data'),
    [Input('dropdown_summoner', 'value')]
)

# function to allow for dynamic interaction
def filter_table(x):
    filter_df = df_table

    if x is not None and x != '':
        filter_df = filter_df[filter_df['Summoner Name'] == x]

    return filter_df.to_dict('records')

# executing application
# note if webpage is loaded up before execution has finished error should occur. refresh webpage for fix.
if __name__ == '__main__':
    app.run_server(debug=False)