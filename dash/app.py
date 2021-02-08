
#file for everything related to exploration and graphs

import pandas as pd
import json
import configparser
from random import randint

import plotly.express as px
from plotly.graph_objects import Bar 

import dash
import dash_core_components as dcc 
import dash_html_components as html
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output



#read in the data

#shapefiles as geojson
with open("data/geometrie.geojson") as f:
    geojs = json.load(f)

#wahlkreise
wahl_df = pd.read_csv("data/wahlkreise.csv")
wahl_df = wahl_df.drop(columns = ["Unnamed: 0"])

#twitter daten
t_df = pd.read_csv("data/accounts_data.csv")
t_df = t_df.drop(columns = ["Unnamed: 0"])
#t_df = t_df.set_index("name_id")

bg_col = "#F9F9F9"
font_col = "black"


def mapbox_auth():
    #authenticate with the mapbox API
    config = configparser.ConfigParser()		
    config.read("config.ini")

    mapbox_token = config["mapbox"]["api_key"]
    px.set_mapbox_access_token(mapbox_token)

#deutschlandkarte
def figure_generator(dataframe, color_column = "twitter"):

    c_map = {
            "CDU": "black",
            "SPD": "#ff3333",
            "GRueNE": "limegreen",
            "AfD": "cornflowerblue",
            "FDP": "gold",
            "DIE LINKE": "#b30000",
            "CSU": "grey",}

    fig = px.choropleth_mapbox(
        dataframe, geojson = geojs, 
        featureidkey = "properties.WKR_NR", 
        locations = "WKR_NR", 
        custom_data= ["WKR_NR", "name_id", color_column],
        color = color_column, color_discrete_map=c_map,
        #color_discrete_sequence=["green", "red"],
        )

    fig.update_traces(
        hovertemplate = "<b>Wahlkreis : %{customdata[0]}</b>  <br>Vertreter: %{customdata[1]} <br> partei: %{customdata[2]} "
    )


    margins = {"t": 0,"b": 0, "l": 0, "r": 0}

    fig.update_layout(
        margin = margins,

        mapbox = {
        "center": {"lon": 10.447 , "lat": 51.1633},
        "zoom": 4.7 },

        mapbox_style = "light",
        showlegend = False
        )
    return fig

#hashtags
def get_hashtags(dataframe):

    """ extract the hastgas out of a given dataframe , not a row
        returns the all hashtags and their counts"""

    hs = dataframe.hashtags.dropna()
    hs = hs.apply(lambda x: x.split(", "))
    hs = hs.explode()
    hs = hs.value_counts()

    hs = hs.mask(hs.index == "")
    hs = hs.dropna()

    return hs

#kategorisierer 
def nutzungsart(t_df, user_row):
    """ func to get the usage behavior of user, takes as input a row,
    returns a label and description"""

    limit_1 = t_df.tweet_rate.describe()["75%"] #meinungsmacher
    limit_2 = t_df.retweet_rate.describe()["75%"] # verbreiter
    limit_3 = t_df.replie_rate.describe()["75%"] # kommunizierer

    if user_row.replie_rate.item() > limit_3:
        text = f"{user_row.replie_rate.item() * 100}% der tweets sind antworten auf andere Nutzern"
        return ("Kommunizierer", text )

    elif user_row.retweet_rate.item() > limit_2:
        text = f"{user_row.retweet_rate.item() * 100}% der tweets sind retweets von anderen Nutzern"
        return ("Verbreiter", text)

    elif user_row.tweet_rate.item() > limit_1:
        text = f"{user_row.tweet_rate.item() * 100}% der tweets sind eigene Meinungen"
        return ("Meinungsmacher", text)

    else:
        text = "nutzt alle funktionen ungefähr gleichviel, nichts sticht heraus"
        return("Allesnutzer", text)

#
def sentiment(user_row):
    sent = user_row.avg_sent.item()
    if sent > 0.1:
        text = "Tweets sind im Schnitt eher gutgelaunt"
        bez = "Gutmütig"

    elif sent < -0.1:
        text = "Tweets sind im Schnitt eher schlechtgelaunt"
        bez = "Grummen"
    else:
        text = "Tweets sind meistens neutral oder schwer einordbar"
        bez = "neutral"
    return (bez,text)

#helper function for color bar 
def get_top(df, col):
    df = df.sort_values(by = col, ascending = False)
    return df

#function returns a bar with the top users in the specified metric
def color_bar(df, col, num = 10):

    sorted = get_top(df, col)
    sorted = sorted[sorted.num_tweets > 5]
    sorted = sorted.reset_index()
    sorted = sorted[:num]
    
    margins = {"t": 0, "r": 0, "l": 0, "b": 0}
    c_map = {
        "cdu": "black",
        "spd": "#ff3333",
        "gruene": "limegreen",
        "afd": "cornflowerblue",
        "fdp": "gold",
        "linke": "#b30000",
        "csu": "dimgray",}
    
    fig = px.bar(
        sorted, y = col, color="partei", #to change layout to quer y = col
        color_discrete_map=c_map, custom_data=["name_id", col], 
        labels = {"_index": "platzierung"},
        height = 70,
        )
    
    fig.update_layout(
        margin = margins, 
        paper_bgcolor = bg_col,
        plot_bgcolor = bg_col, 
        font_color = font_col, 
        showlegend = False
    )
    fig.update_traces(hovertemplate = "%{customdata[0]} <br> Anzahl: %{customdata[1]} ", 
        text = list(range(1,11)), textposition= "auto")

    fig.update_xaxes(visible= False)
    fig.update_yaxes(visible= False)
    return fig

#returns treemap from party followers
def get_treemap(dataframe):
    """ function to get treemap figure, return px.fig"""
    c_map = {
            '(?)':"#F7F7F7",
            "bundestag": bg_col,
            "cdu": "black",
            "spd": "#ff3333",
            "gruene": "limegreen",
            "afd": "cornflowerblue",
            "fdp": "gold",
            "linke": "#b30000",
            "csu": "dimgray",}

    fig = px.treemap(
        dataframe, path = ["bundestag", "partei", "name_id"], values = "num_followers", 
        color = "partei", color_discrete_map = c_map, 
        custom_data=["num_followers"], height=300,
        )

    margins = {"t": 20, "r": 0, "l": 0, "b": 0}
    fig.update_layout(margin = margins, paper_bgcolor= "#F9F9F9")

    fig.update_traces(hovertemplate = " Follower: %{customdata[0]}")

    return fig

#horizontal
def horizontal(dataframe, partei):

    c_map = {
            "bundestag": "grey",
            "cdu": "black",
            "spd": "#ff3333",
            "gruene": "limegreen",
            "afd": "cornflowerblue",
            "fdp": "gold",
            "linke": "#b30000",
            "csu": "dimgray",}

    anzahl = {
        "bundestag": 709,
        "spd": 152,
        "cdu": 200,
        "fdp": 80,
        "afd": 88,
        "linke": 69,
        "gruene":67,
        "csu": 46
    }

    zahl = sum(dataframe.partei == partei)
    if partei == "bundestag":
        zahl = len(dataframe)
    prozent = int(zahl /anzahl[partei] * 100)

    fig = px.bar(
        height = 50, 
        color = [c_map[partei]], opacity=0.5
    )
    fig.add_trace(
        Bar(x = [anzahl[partei]], marker = dict(color = c_map[partei], opacity = 0.5), hovertemplate = "MdBs: %{x}")
    )
    fig.add_trace(
        Bar(x = [zahl], marker = dict(color = [c_map[partei]]), hovertemplate = "MdBs mit Twitter: %{x}", 
        text = f"Prozent an Abgeordneten mit Twitter: {prozent} %", textposition = "auto")
    )

    margins = {"t": 0, "r": 0, "l": 10, "b": 0}
    fig.update_layout(barmode = "overlay", margin = margins,
        plot_bgcolor= bg_col, showlegend= False)

    fig.update_yaxes(visible = False)
    fig.update_xaxes(visible = False)
    return fig

#positionsbestimmer
def get_pos(search_column, value):
    """function to get position of a value in column and a corespoding color """
    column = search_column.sort_values(ascending = False, ignore_index = True)
    i = column[column == value].index[0]
    l = len(column)

    colors = ["#2B8B0F","#A7C306","#E0CD20","#D58B10","#CF492D"]

    #returns the füfntel in which the value lies to index the color list
    cindex = int(i/(l/5))
    c = colors[cindex]

    text = f"#{i} von {l}"
    return (text,c)

#user div generation
def user_generator(df, user):
    row = t_df[t_df.name_id == user]
    art = nutzungsart(df, row)
    sent = sentiment(row)
    #hashtags =  row.hashtags.split(", ") #hashtags from a user row



    #poses = [get_pos()]
    pos = get_pos(t_df.num_followers, row.num_followers.item())

    div = html.Div(children = [
        html.Div(className = "pretty_container", children = [
            html.H5(row.name),
            html.B(row.name_id),
            html.P(row.desc),

            #first row
            html.Div(className = "row", children = [
                html.Div(className = "four columns bare_container", children = [
                    html.B("followers:"),
                    html.P(row.num_followers),
                    html.P(pos[0]),
                ], style = {"color": pos[1]}),

                html.Div(className = "four columns bare_container", children = [
                    html.B("following:"),
                    html.P(row.num_following)
                ]),

                html.Div(className = "one-third column bare_container", children = [
                    html.B("Tweets"),
                    html.P(row.num_tweets)
                ]),
            ]),

            #second row
            html.Div(className = "row", children = [
                html.Div(className = "four columns bare_container", children = [
                    html.B("tweets/tag:"),
                    html.P(round(row.ts_perday, 2)),
                ]),

                html.Div(className = "four columns bare_container", children = [
                    html.B("erstelldatum:"),
                    html.P(row.created_at.item()[:10]),
                ]),

                html.Div(className = "one-third column bare_container", children = [
                    html.B("Laune"),
                    html.P(sent[0]),
                    #html.P(sent[1])
                ]),
            ]),

            #zuletzt aktualisiert
            html.Div(className = "twelve columns bare_container", children = [
                html.B(art[0]),
                html.P(art[1]),
            ]),

            html.P(f"zuletzt aktualisiert: {randint(10,24)}:{randint(10,60)}")
        ]),


    ])
    return div


    



mapbox_auth()

t_df["bundestag"] = "Followerzahlen des Bundestages"
df = pd.merge(wahl_df, t_df, how = "inner", on="name_id")


app = dash.Dash(
    __name__, title = "twitter", meta_tags=[{"name": "viewport", "content": "width=device-width"}]
    )
#server = app.server

app.layout = html.Div( children = [

    
    html.Div(className = "row", children = [

        #first row
        html.Div(className = "four columns", children = [

            html.Div(className = "pretty_container",children = [
                html.H1("Bundestwitter"),
                html.P("Fast 80% der Abgeordneten haben Twitter, aber nur 5% der Deutschen. \
                    Stellt sich die Frage, was die da eigentlich machen. Hier ist die Antwort"
                )
            ], #style = {"height": "50%"}
            ),

            html.Div(className = "pretty_container", children = [

                html.H1("Leaderboards"),

                dcc.Dropdown(id = "drop1", 
                    options = [
                        {"label":"anzahl tweets", "value": "num_tweets" },
                        {"label":"abonnenten", "value": "num_followers"},
                        {"label":"abonniert", "value": "num_following"},
                    ], value = "num_tweets"
                ), 

                dcc.Graph(id = "bar1",
                    #figure = color_bar(t_df, "num_tweets"),
                    config = {"displayModeBar": False}
                ),

                html.Br(),

                dcc.Dropdown(id = "drop2",
                    options = [
                        {"label":"Kommunizierer", "value": "replie_rate"},
                        {"label":"Meinungsmacher", "value": "tweet_rate"},
                        {"label":"Verbreiter", "value":"retweet_rate" },
                    ], value = "replie_rate",
                ),

                dcc.Graph(id = "bar2",
                    #figure = color_bar(t_df, "replie_rate"),
                    config = {"displayModeBar": False}
                ),
            
            ]),
         
        ]),

        #second row
        html.Div(className = "four columns pretty_container", children = [

            html.Div(children = [
                dcc.Graph(
                    #figure = figure_generator(df, "partei_x")
                )
            ]),

            html.Div(children = [
                dcc.Graph(
                    figure = get_treemap(t_df)
                )
            ]),

            html.Div(children = [
                dcc.Graph(
                    figure = horizontal(t_df, "spd"), config = {"responsive": False, "displayModeBar": False}
                )
            ])


        ], style = {"padding": "0px"}),
        
        #third row
        html.Div(className = "four columns", children = [

            html.Div(className = "pretty_container", children = [
                html.H6("Nutzer wählen"),
                html.B("Ausgewählter Nutzer"),

            ]),

            html.Div(children = [
                user_generator(t_df, "@johannesvogel")

            ]),
        ]),


    ]),

])

@app.callback(
    Output("bar1", "figure"),
    Output("bar2", "figure"),

    Input("drop1", "value"),
    Input("drop2", "value"),
)

def update_bars(val1, val2):
    figure1 = color_bar(t_df, val1)
    figure2 = color_bar(t_df, val2)

    return figure1, figure2

if __name__ == "__main__":
    app.run_server(debug=True)
