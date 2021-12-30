import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)

df = pd.read_json('datahub/validated/match_dataset.json')



app.layout = html.Div([
    dcc.Graph(id = 'graph',
        figure = px.scatter(x = df['wins'], y = df['losses'])
        )
    ])
if __name__ == '__main__':
    app.run_server(debug=True)