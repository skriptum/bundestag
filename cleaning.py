#%%



#general file to clean up geometric data and data from the wahlkreisergebnisse

#import necessary modules
import pandas as pd
import json
import configparser


#%%
#read in the data

#twitter account data
df = pd.read_csv("data/accounts_data.csv")
df = df.drop(columns = ["Unnamed: 0"])


#wahlkreise wahlergebnisse
wahl = pd.read_csv("data/wahl.csv", sep = ";", encoding="utf8")


#better wahl data
wahl["Namen"] = wahl["Vorname"] + " " + wahl["Name"]
wahl = wahl.drop(columns=["Geburtsjahr", "Beruf", "Wiedergewählt", "Vorname", "Name"])
wahl = wahl.dropna()
wahl = wahl.rename(columns = {"Gewählt_Wahlkreis_Nr": "WKR_NR"} )

#%%
# #verbindung von Wahlkreisen und Twitter Handels, falls benötigt


#namen der Wahlergebniss datei und namen der Twitter Datei
namen1 = df.loc[:,"name_id": "id"]
namen2 = wahl.Namen 


#eine Datei erstellen, bei der soviel wie möglich verbunden wurde von beiden
int_df = pd.merge(namen1,namen2, left_on="screen_name", right_on="Namen", how = "right" )
int_df.to_csv("data/verbindung.csv")
#jetzt muss per Hand nachgearbeitet werden und fehlende sachen verbunden werden


#%%

#read in verbindungsdaten again
ver = pd.read_csv("data/verbindung.csv", sep = ";")


#merge back verbindungsdaten und wahldaten
gp = pd.merge(ver, wahl, on = "Namen", how = "inner")


#creating new columns for better mapping
gp["twitter"] = gp.name_id.notna()
gp["twitter"] = gp.twitter*1

#cle
# aning up the data
gp = gp.drop(columns=["Gewählt_Land", "Unnamed: 0"])
gp = gp.rename( columns={
    "Partei_KurzBez": "partei", "Gewählt_Wahlkreis_Bez":"wahlkreis"
    })

gp.to_csv("data/wahlkreise.csv")


# %%
