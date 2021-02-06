
#file for everything related to exploration and graphs

import pandas as pd
import json
import configparser

import plotly.express as px

import dash
import dash_core_components as dcc 
import dash_html_components as html
import dash_bootstrap_components as dbc 




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
            "SPD": "crimson",
            "GRueNE": "limegreen",
            "AfD": "cornflowerblue",
            "FDP": "gold",
            "DIE LINKE": "brown",
            "CSU": "dimgray",}

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

    return hs

#kategorisierer 
def nutzungsart(t_df, user_row):
    """ func to get the usage behavior of user, takes as input a row,
    returns a label and description"""

    limit_1 = t_df.tweet_rate.describe()["75%"] #meinungsmacher
    limit_2 = t_df.retweet_rate.describe()["75%"] # verbreiter
    limit_3 = t_df.replie_rate.describe()["75%"] # kommunizierer

    if user_row.replie_rate > limit_3:
        text = f"{user_row.replie_rate * 100}% der tweets sind antworten auf andere Nutzern"
        return ("Kommunizierer", text )

    elif user_row.retweet_rate > limit_2:
        text = f"{user_row.retweet_rate * 100}% der tweets sind retweets von anderen Nutzern"
        return ("Verbreiter", text)

    elif user_row.tweet_rate > limit_1:
        text = f"{user_row.tweet_rate * 100}% der tweets sind eigene Meinungen"
        return ("Meinungsmacher", text)

    else:
        text = "nutzt alle funktionen ungefähr gleichviel, nichts sticht heraus"
        return("Allesnutzer", text)

#helper function for color bar 
def get_top(df, col):
    df = df.sort_values(by = col, ascending = False)
    return df

#function returns a bar with the top users in the specified metric
def color_bar(df, col, num = 20):

    sorted = get_top(df, col)
    sorted = sorted[sorted.num_tweets > 5]
    sorted = sorted.reset_index()
    sorted = sorted[:num]
    
    margins = {"t": 0, "r": 0, "l": 0, "b": 0}
    c_map = {
        "cdu": "black",
        "spd": "crimson",
        "gruene": "limegreen",
        "afd": "cornflowerblue",
        "fdp": "gold",
        "linke": "brown",
        "csu": "dimgray",}
    
    fig = px.bar(
        sorted, y = col, color="partei", #to change layout to quer y = col
        color_discrete_map=c_map, custom_data=["name_id", col], 
        labels = {"_index": "platzierung"},
        height = 300,
        )
    
    fig.update_layout(
        margin = margins, 
        paper_bgcolor = bg_col,
        plot_bgcolor = bg_col, 
        font_color = font_col, 
        showlegend = False
    )
    fig.update_traces(hovertemplate = "%{customdata[0]} <br> Anzahl: %{customdata[1]} ")

    fig.update_xaxes(visible= False)
    fig.update_yaxes(visible= False)
    return fig

#returns treemap from party followers
def get_treemap(dataframe):
    """ function to get treemap figure, return px.fig"""
    c_map = {
            '(?)':"#F9F9F9",
            "bundestag": bg_col,
            "cdu": "black",
            "spd": "crimson",
            "gruene": "limegreen",
            "afd": "cornflowerblue",
            "fdp": "gold",
            "linke": "brown",
            "csu": "dimgray",}

    fig = px.treemap(
        dataframe, path = ["bundestag", "partei", "name_id"], values = "num_followers", 
        color = "partei", color_discrete_map = c_map, 
        custom_data=["num_followers"], height=300,
        )

    margins = {"t": 0, "r": 0, "l": 0, "b": 0}
    fig.update_layout(margin = margins, paper_bgcolor= "#F9F9F9")

    fig.update_traces(hovertemplate = " Follower: %{customdata[0]}")

    return fig



mapbox_auth()

t_df["bundestag"] = "Followerzahlen des Bundestages"
df = pd.merge(wahl_df, t_df, how = "inner", on="name_id")


# fig = figure_generator(t_wahl_df, "partei_x")
#fig.show()

# user layout

# user = "@johannesvogel"
# row = t_df[t_df.name_id == user]
# hashtags =  row.hashtags.split(", ") #hashtags from a user row





app = dash.Dash(
    __name__, title = "twitter", meta_tags=[{"name": "viewport", "content": "width=device-width"}]
    )

server = app.server

app.layout = html.Div( children = [

    # html.Div(className = "row", children = [
    #     html.Div(className = "pretty_container",children = [

    #         html.H1("TITLE"),
    #         html.P("hello"),

    #     ])
    # ]),
    
    html.Div(className = "row", children = [

        html.Div(className = "three columns", children = [

            html.Div(className = "pretty_container",children = [
                html.H1("Bundestwitter"),
                html.P("Fast 80% der Abgeordneten haben Twitter, aber nur 5% der Deutschen. \
                    Stellt sich die Frage, was die da eigentlich machen. Hier ist die Antwort"
                )
            ]),

            html.Div(className = "pretty_container",children = [
                html.H3("Ausgewählter Nutzer"),

                dbc.Card(
                    dbc.CardBody(children = [
                        html.H4("user", className = "card_title"),
                        html.P(html.B("@username")),
                        html.P( " description of the current user .....", className = "card_text"),
                    ]),
                ),
            ]),

            
        ]),

        html.Div(className = "five columns pretty_container", children = [

            html.Div(children = [
                dcc.Graph(
                    figure = figure_generator(df, "partei_x")
                )
            ]),

            html.Div(children = [
                dcc.Graph(
                    figure = get_treemap(t_df)
                )
            ]),


        ]),
        
        html.Div(className = "four columns", children = [

            html.Div(className = "pretty_container", children = [
                html.H1("Leaderboards"),
                dcc.Graph(
                    figure = color_bar(t_df, "ts_perday")
                )
            ]),

            html.Div(className = "pretty_container", children = [
                html.H1("Hashtags")
            ]),

        ]),


    ]),

])

if __name__ == "__main__":
    app.run_server(debug=True)
