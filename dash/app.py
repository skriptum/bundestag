
#file for everything related to exploration and graphs

import pandas as pd
import json
import configparser
from collections import Counter

import plotly.express as px
from plotly.graph_objects import Bar 

import dash
import dash_core_components as dcc 
import dash_html_components as html
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output, State


#read in the data

#shapefiles as geojson
with open("data/geometrie2.geojson") as f:
    geojs = json.load(f)

#wahlkreise
wahl_df = pd.read_csv("data/wahlkreise.csv")
wahl_df = wahl_df.drop(columns = ["Unnamed: 0"])

#twitter daten
t_df = pd.read_csv("data/accounts_data.csv")
t_df = t_df.drop(columns = ["Unnamed: 0"])
#t_df = t_df.set_index("name_id")

bg_col = "#F9F9F9"

c_map = {
            '(?)':"#F7F7F7",
            "bundestag": "rgba(246, 232, 223, 0.89)",
            "cdu": "rgba(37, 35, 33, 0.8)",
            "spd": "rgba(238, 12, 45, 0.8)",
            "gruene": "rgba(169, 218, 20, 0.8)",
            "afd": "rgba(76, 156, 227, 0.8)",
            "fdp": "rgba(255, 217, 15, 0.8)",
            "linke": "rgba(196, 25, 25, 0.8)",
            "csu": "rgba(153, 177, 187, 0.8)",
        }


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
        custom_data= ["wahlkreis", "name_id", color_column],
        color = color_column, color_discrete_map=c_map,
        opacity=0.5,
        )

    fig.update_traces(
        hovertemplate = "<b>Abgeordneter : %{customdata[1]}</b>  <br>%{customdata[0]} <br>Partei: %{customdata[2]} "
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
        text = f"{round(user_row.replie_rate.item() * 100)}% der tweets sind antworten auf andere Nutzern"
        return ("Kommunizierer", text )

    elif user_row.retweet_rate.item() > limit_2:
        text = f"{round(user_row.retweet_rate.item() * 100)}% der tweets sind retweets von anderen Nutzern"
        return ("Verbreiter", text)

    elif user_row.tweet_rate.item() > limit_1:
        text = f"{round(user_row.tweet_rate.item() * 100)}% der tweets sind eigene Meinungen"
        return ("Meinungsmacher", text)

    else:
        text = "nutzt alle funktionen ungefähr gleichviel, nichts sticht heraus"
        return("Allesnutzer", text)

#
def sentiment(user_row):
    sent = user_row.avg_sent.item()

    sent_colors = {
        "Gutmütig": "#2B8B0F",
        "Grummel": "CF492D",
        "neutral": "#f0ead6"
    }
    if sent > 0.1:
        text = "∅ eher gutgelaunt"
        bez = "Gutmütig"

    elif sent < -0.5:
        text = "∅ eher schlechtgelaunt"
        bez = "Grummel"
    else:
        text = "neutral /nicht einordbar"
        bez = "neutral"
    return (bez,text, sent_colors[bez])

#helper function for color bar 
def get_top(df, col):
    df = df.sort_values(by = col, ascending = False)
    return df

#function returns a bar with the top users in the specified metric
def color_bar(df, col, c_map):

    sorted = get_top(df, col)
    sorted = sorted[sorted.num_tweets > 5]
    sorted = sorted.reset_index()
    sorted = sorted[:10]
    
    margins = {"t": 0, "r": 0, "l": 0, "b": 0}
    
    fig = px.bar(
        sorted, y = col, color="partei", #to change layout to quer y = col
        color_discrete_map=c_map, custom_data=["name_id", col], 
        labels = {"_index": "platzierung"},
        height = 100,
        )
    
    fig.update_layout(
        margin = margins, 
        paper_bgcolor = bg_col,
        plot_bgcolor = bg_col, 
        showlegend = False
    )
    fig.update_traces(hovertemplate = "%{customdata[0]} <br> Anzahl: %{customdata[1]} ", 
        texttemplate = "%{customdata[0]}", textposition= "auto")

    fig.update_xaxes(visible= False, fixedrange = True)
    fig.update_yaxes(visible= False, fixedrange = True)
    return fig

#returns treemap from party followers
def get_treemap(dataframe, c_map):
    """ function to get treemap figure, return px.fig"""

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
def horizontal(dataframe, partei, c_map):


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
        height = 40, 
        color = [c_map[partei]], opacity=0.5
    )
    fig.add_trace(
        Bar(x = [anzahl[partei]], marker = dict(color = c_map[partei], opacity = 0.5, line_color = "black"), hovertemplate = "MdBs: %{x}")
    )
    fig.add_trace(
        Bar(x = [zahl], marker = dict(color = [c_map[partei]], line_color = "black"), hovertemplate = "MdBs mit Twitter: %{x}", 
        text = f"{partei}-Mitglieder mit Twitter: {prozent} %", textposition = "auto"),
    )

    margins = {"t": 0, "r": 0, "l": 10, "b": 5}
    fig.update_layout(barmode = "overlay", margin = margins,
        plot_bgcolor= bg_col, showlegend= False)

    fig.update_yaxes(visible = False, fixedrange = True)
    fig.update_xaxes(visible = False, fixedrange = True)
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
def user_generator(df, user, c_map):
    row = df[df.name_id == user]

    if row.num_tweets.item() == 0:
        div = html.Div(className = "pretty_container", children = [

            html.H4("Twitter Profil:"),

            html.Div(className = "bare_container", children = [
                html.H5(row.name),
                html.B(row.name_id),
                html.P(row.desc),
            ]),

            html.B("Hat noch keinen einzigen tweets"),
        ])

        return div
    
    art = nutzungsart(df, row)
    sent = sentiment(row)

    if row.hashtags.isna().any():
        hashtags = "nutzer hat keine hashtags gepostet"
        h_div = html.Div(className = "bare_container", children = [html.P(hashtags)])

    else:
        hs_list =  row.hashtags.item().split(", ")[:-1] #hashtags from a user row
        hs_nested = Counter(hs_list).most_common(5)
        childs = [html.B("Hashtags"),]
        for tup in hs_nested:
            childs.append(html.P(f"{tup[0]}: {tup[1]} Mal "))

        h_div = html.Div(className = "bare_container", children = childs)
        

    #poses = [get_pos()]
    pos_flws = get_pos(df.num_followers, row.num_followers.item())
    pos_tspd = get_pos(df.ts_perday, row.ts_perday.item())
    pos_fling = get_pos(df.num_following, row.num_following.item())
    pos_ts = get_pos(df.num_tweets, row.num_tweets.item())

    div = html.Div(children = [
        html.Div( children = [

            html.Div(className = "bare_container", children = [
                html.H5(row.name),
                html.B(row.name_id),
                html.P(row.desc.item()),
            ]),

            #first row
            html.Div(className = "row", children = [
                html.Div(className = "four columns bare_container", children = [
                    html.B("Abonnenten"),
                    html.P(row.num_followers),
                    html.P(pos_flws[0]),
                ], style = {"background-color": pos_flws[1]}),

                html.Div(className = "four columns bare_container", children = [
                    html.B("hat abonniert"),
                    html.P(row.num_following),
                    html.P(pos_fling[0]),
                ], style = {"background-color": pos_fling[1]}),

                html.Div(className = "one-third column bare_container", children = [
                    html.B("Tweets"),
                    html.P(row.num_tweets),
                    html.P(pos_ts[0]),
                ], style = {"background-color": pos_ts[1]}),
            ]),

            #second row
            html.Div(className = "row", children = [
                html.Div(className = "four columns bare_container", children = [
                    html.B("tweets/tag:"),
                    html.P(round(row.ts_perday, 2)),
                    html.P(pos_tspd[0])
                ], style = {"background-color": pos_tspd[1]}
                ),

                html.Div(className = "four columns bare_container", children = [
                    html.B("Laune"),
                    #html.P(sent[0]),
                    html.P(sent[1])
                ], style = {"background-color": sent[2]}),

                html.Div(className = "one-third column bare_container", children = [
                    html.B("Partei"),
                    html.P(row.partei.item()),
                ], style = {"background-color": c_map[row.partei.item()], "color": "white", "border-color": "black"}),
            ]),

            #zuletzt aktualisiert
            html.Div(className = "bare_container", children = [
                html.B(art[0]),
                html.P(art[1]),
            ]),

            h_div,
            html.P("yeet")
        ]),


    ])
    return div

mapbox_auth()

t_df["bundestag"] = "Bundestag gesamt:"
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

                html.H4("Leaderboards"),

                dcc.Dropdown(id = "drop1", 
                    options = [
                        {"label":"anzahl tweets", "value": "num_tweets" },
                        {"label":"abonnenten", "value": "num_followers"},
                        {"label":"abonniert", "value": "num_following"},
                    ], value = "num_tweets", clearable = False,
                ), 

                dcc.Graph(id = "bar1",
                    
                    config = {"displayModeBar": False, "responsive": False, "displaylogo": False}
                ),

                html.Br(),

                dcc.Dropdown(id = "drop2",
                    options = [
                        {"label":"Kommunizierer", "value": "replie_rate"},
                        {"label":"Meinungsmacher", "value": "tweet_rate"},
                        {"label":"Verbreiter", "value":"retweet_rate" },
                    ], value = "replie_rate", clearable = False,
                ),

                dcc.Graph(id = "bar2",
                    
                    config = {"displayModeBar": False, "displaylogo": False, "responsive": False}
                ),
            
            ]),
         
        ]),

        #second row
        html.Div(className = "four columns", children = [

            html.Div(className = "pretty_container", children = [
                dcc.Graph(id = "wahl_map",
                    figure = figure_generator(df, "partei_x"),
                    config = {"displaylogo": False}
                )
            ], style = {"padding": "0px"}),

            html.Div(className = "pretty_container", children = [
                html.H4("Followervergleich", style = {"margin": 10, "margin-bottom": 0, "margin-top": 0}),
                dcc.Graph(id = "tree_map",
                    figure = get_treemap(t_df, c_map),
                    config = {"displaylogo": False}
                ),
            
                dcc.Graph(id = "horizontal",
                config = {"responsive": False, "displayModeBar": False}
                )
            ], style = {"padding": "0px"}),


        ]),
        
        #third row
        html.Div(className = "four columns", children = [

            html.Div( className = "pretty_container", children = [
                html.H4("nutzer"),
                dcc.Input(id = "text-input", 
                    type = "text", placeholder = "schreiben"
                ),
                html.Button("submit", id = "submit-button", n_clicks = 0),

                html.Div(id = "select-out"),
            ]),

            html.Div(id = "user-div", className = "pretty_container", children = [
                user_generator(t_df, "@johannesvogel", c_map)

            ]),
        ]),


    ]),

])





#dropwdown on bars callback
@app.callback(
    Output("bar1", "figure"),
    Output("bar2", "figure"),

    Input("drop1", "value"),
    Input("drop2", "value"),
)

def update_bars(val1, val2):
    figure1 = color_bar(t_df, val1, c_map)
    figure2 = color_bar(t_df, val2, c_map)

    return figure1, figure2

#user select callback
@app.callback(
    Output("user-div", "children"),
    Output("select-out", "children"),

    Input("wahl_map", "clickData"),
    Input("submit-button", "n_clicks"),
    State("text-input", "value"),

)
def user_select(map_click, clicked, text_in):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if "wahl_map" in changed_id:
        user = map_click["points"][0]["customdata"][1]
        profil = user_generator(t_df, user, c_map)

    elif "submit-button" in changed_id:
        user = text_in
        profil = user_generator(t_df, user, c_map)

    else:
        user = t_df.name_id.sample().item()
        profil = user_generator(t_df, user, c_map)

    out = f"{user}"
    return profil, out

#treemap callback
@app.callback(
    Output("horizontal", "figure"),
    Input("tree_map", "clickData"),
)
def update_horizontal(clickData):
    try:
        p = clickData["points"][0]["customdata"][1]
        if p == '(?)':
            p = "bundestag"
    except:
        p = "bundestag"

    figure = horizontal(t_df, p, c_map)
    return figure




if __name__ == "__main__":
    app.run_server(debug=True)
