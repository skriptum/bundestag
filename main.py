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

#%%

#authenticate with the mapbox API
config = configparser.ConfigParser()		
config.read("config.ini")

mapbox_token = config["mapbox"]["api_key"]
px.set_mapbox_access_token(mapbox_token)

#%%

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

# %%
t_wahl_df = pd.merge(wahl_df, t_df, how = "inner", on="name_id")

# fig = figure_generator(t_wahl_df, "partei_x")
#fig.show()
# %%
#possible metrics 
#       'retweet_rate', 'replie_rate', 
#       'ts_perday', 'hashtags',
#       'avg_sent', 
#
#       num_followers, num_following, created_at


# 20 meistgenutze hashtags
h = t_df.hashtags[0].split(", ")[:-1]



# %%
#kommunizierer = replie rate > 0.35
# papageien =  retweet-rate > 0.5
#meinungsmacher = tweet_rate > 0.75

# aktive = ts_perday > 3
#inaktiv 