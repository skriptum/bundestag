#%%
import tweepy 
import pandas as pd
import os


#%%
#Keysaving

consumer_key = "zLhaEr6YbhAyUJDKykXt7rShh"

consumer_secret = "A8WoN8CERsebjyGAvTAVCDiDtixB5mQenvuszFxQ2A3YF4yc2Q"

# %%
#Authentication with API
auth = tweepy.AppAuthHandler(consumer_key,consumer_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
Cursor = tweepy.Cursor


#%%
#create the central dataframe for storing everything
data = pd.DataFrame(columns = 
                    ["screen_name", "id", "desc", "creation_date", "profile_pic",
                     "num_followers", "num_following", "num_tweets"])


#%%
#get every mdb and his party from  astored text file

os.chdir("/Users/code/Desktop/bundestag/partei")
dict = {}
files = os.listdir()[1:]
for parteifile in files:
    with open(parteifile) as partei:
        for line in partei:
            line =  line.strip("\n")
            dict[line] = parteifile[:-4]

data2 = pd.DataFrame.from_dict(dict,orient="index", columns =  ["partei"])
os.chdir("..")

data = data.append(data2)
data = data.reset_index()
data.rename(columns = {"index":"name_id"}, inplace = True)
# %%
#run trough every mdb

for i in range(len(data.index)):

    username = data["name_id"][i]
    partei = data["partei"][i]
    target = api.get_user(id = username)
    
    #some general info about the user
    name = target.name
    creation_date = target.created_at
    profile_pic =  target.profile_image_url_https
    desc = target.description
    id = target.id
    name = target.name
    num_followers = target.followers_count
    num_following = target.friends_count
    num_tweets = target.statuses_count

    #add data to dataframe
    data.iloc[i] = [username, name, id, desc, creation_date,
                    profile_pic, num_followers, 
                    num_following, partei]

data.to_csv("accounts_data.csv")