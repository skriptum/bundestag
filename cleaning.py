
#%%
import pandas as pd
import plotly.express as px
import json
import configparser

#%%
config = configparser.ConfigParser()		
config.read("config.ini")

mapbox_token = config["mapbox"]["api_key"]
px.set_mapbox_access_token(mapbox_token)

#%%
#twitter account data
df = pd.read_csv("data/accounts_data.csv")
df = df.drop(columns = ["Unnamed: 0"])

#wahlkreise wahlergebnisse
wahl = pd.read_csv("data/wahl.csv", sep = ";", encoding="utf8")

#shapefiles as geojson
with open("data/geometrie.geojson") as f:
    geojs = json.load(f)


#better wahl data
wahl["Namen"] = wahl["Vorname"] + " " + wahl["Name"]
wahl = wahl.drop(columns=["Geburtsjahr", "Beruf", "Wiedergewählt", "Vorname", "Name"])
wahl = wahl.dropna()
wahl = wahl.rename(columns = {"Gewählt_Wahlkreis_Nr": "WKR_NR"} )

#%%
# #verbindung von Wahlkreisen und Twitter Handels, falls benötigt

# wahl = pd.read_csv("data/wahl.csv", sep = ";", encoding="utf8")
# wahl["Namen"] = wahl["Vorname"] + " " + wahl["Name"]

# namen1 = data.loc[:,"name_id": "id"]
# namen2 = wahl.Namen 

# int_df = pd.merge(namen1,namen2, left_on="screen_name", right_on="Namen", how = "right" )
# int_df.to_csv("data/verbindung.csv")
#jetzt muss per Hand nachgearbeitet werden und fehlende sachen verbunden werden


#wahlkreise und twitter verbindung neu laden nach verbesserung
ver = pd.read_csv("data/verbindung.csv", sep = ";")




#%%
#merge data

gp = pd.merge(ver, wahl, on = "Namen", how = "inner")
#creating new columns 
gp["Kreis"] = gp.WKR_NR -1
gp["twitter"] = gp.name_id.notna()
gp["twitter"] = gp.twitter*1

gp = gp.drop(columns=["Gewählt_Land", "Unnamed: 0"])
# %%
#figure
fig = px.choropleth_mapbox(
    gp, geojson = geojs, featureidkey = "properties.WKR_NR", locations = gp.WKR_NR, 
    color = gp.Partei_KurzBez,hover_name = gp.name_id
    )

fig.update_layout(mapbox = {
    "center": {"lon": 10.447 , "lat": 51.1633},
    "zoom": 4

    })
fig.show()

# %%
