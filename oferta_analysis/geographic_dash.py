
# DASH App for Geographic information of Spain provinces

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import numpy as np
import json
import plotly.express as px

app = Dash(__name__)

# Data input
df_general = pd.read_csv("./spain_offers_general.csv")
df_categories = pd.read_csv("./spain_offers_categories.csv")
file = open('./spain-provinces.geojson')
spain_map = json.load(file)
file.close()

# Base Layout
app.layout = html.Div([
    html.H2('Available Offers by Province in Spain [Infojobs Snapshot]'),

    html.Div([
        html.Div(children=[
            html.Label('Select target Variable:'),
            dcc.Dropdown(['Offers by Province', 'Mean Salary by Province'], 'Offers by Province', id="variable"),
            html.Br(),
            html.Label("Categories"),
            dcc.Dropdown(['Todas'] + list(df_categories['category'].unique()), 'Todas', id = "category"),
        
        ], style={'padding': 5, 'flex': 2,}),

        html.Div(children=[
            #html.H4('Offers for Informáticos y telecomunicaciones'),
            dcc.Graph(id="graph"),
            ], style={'padding': 5, 'flex': 4}),

    
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    ])


@app.callback(Output("graph", "figure"), Input("category", "value"), Input("variable", "value"),)
def display_choropleth(category, variable):
    
    # Preprocess your data
    if category == "Todas": data = df_general
    else: data = df_categories.loc[df_categories['category'] == category]

    data['text'] = "Province " + data['province'].astype(str) +  "<br>" + \
                    "Id " + data['cartodb_id'].astype(str)

    if variable == "Offers by Province": 
        color_variable = "counts"
        color_pallete = "Blues"

    else: 
        color_variable = "salary"
        color_pallete = "Reds"

    # Update the choropleth
    fig = px.choropleth(
        data, 
        geojson=spain_map,
        locations="cartodb_id", 
        featureidkey="properties.cartodb_id",
        color=color_variable,
        color_continuous_scale=color_pallete, 
        projection="mercator", 
        hover_name = 'text',
        hover_data = {'counts' : True, 'salary' : True, 'cartodb_id' : False, 'province' : False},
        labels={'counts':'Total Offers', 'salary' : "Mean Salary"},
    )

    # Centered on spain
    fig.update_geos(
            lonaxis_range = [-10,5], 
            lataxis_range = [35,45],
            resolution = 50, 
            #fitbounds="locations", 
            #visible=False
        )

    fig.update_layout(height = 850)
    #fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)