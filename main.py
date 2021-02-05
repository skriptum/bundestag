#file for everything related to exploration and graphs

#%%
import pandas as pd
import plotly.express as px
import json
import configparser

#%%
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

#%%

def mapbox_auth():
    #authenticate with the mapbox API
    config = configparser.ConfigParser()		
    config.read("config.ini")

    mapbox_token = config["mapbox"]["api_key"]
    px.set_mapbox_access_token(mapbox_token)

#deutschlandkarte
def figure_generator(dataframe, color_column = "twitter"):
    fig = px.choropleth_mapbox(
        dataframe, geojson = geojs, 
        featureidkey = "properties.WKR_NR", 
        locations = "WKR_NR", 
        custom_data= ["WKR_NR", "name_id", color_column],
        color = color_column, 
        #color_discrete_sequence=["green", "red"],
        )

    fig.update_traces(
        hovertemplate = "<b>Wahlkreis : %{customdata[0]}</b>  <br>Vertreter: %{customdata[1]} <br> feature: %{customdata[2]} "
    )


    margins = {"t": 0,"b": 0, "l": 0, "r": 0}

    fig.update_layout(
        margin = margins,

        mapbox = {
        "center": {"lon": 10.447 , "lat": 51.1633},
        "zoom": 4 },

        mapbox_style = "open-street-map",
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
        labels = {"_index": "platzierung"}
        #height = 700, width=300
        )
    fig.update_layout(margin = margins)
    fig.update_traces(hovertemplate = "%{customdata[0]} <br> Anzahl: %{customdata[1]} ")

    return fig




#%%

#get the akcitivity class
labels = ["inaktiv", "wenig aktiv", "aktiv", "sehr aktiv"]
t_df["aktivität"] = pd.qcut(t_df.ts_perday, q = 4, labels = labels)

# row.hashtags.split(", ") #hashtags from a user row

#%%
#cool treemap
c_map = {
        "cdu": "black",
        "spd": "crimson",
        "gruene": "limegreen",
        "afd": "cornflowerblue",
        "fdp": "gold",
        "linke": "brown",
        "csu": "dimgray",}

fig = px.treemap(
    t_df, path = ["partei", "name_id"], values = "num_followers", 
    color = "partei", color_discrete_map = c_map, 
    custom_data=["name_id", "num_followers"]
    )

fig.update_traces(hovertemplate = "<b>%{customdata[0]}</b> <br> Follower: %{customdata[1]}")
fig.show()
# %%
df = pd.merge(wahl_df, t_df, how = "inner", on="name_id")

# fig = figure_generator(t_wahl_df, "partei_x")
#fig.show()