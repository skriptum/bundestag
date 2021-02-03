#%%
import tweepy 
import pandas as pd
import os
from fetch import api_auth

#%%
#get every mdb and his party from  astored text file

def get_users(path_for_files = "/Users/code/Desktop/bundestag/partei"):

    """ get the users located in the subdirectory in txt files
    with the name of the file being their party """

    dict = {}
    files = os.listdir(path_for_files)[1:]
    for parteifile in files:
        with open(parteifile) as partei:
            for line in partei:
                line =  line.strip("\n")
                dict[line] = parteifile[:-4]
    
    return dict


#%%
api = auth()


data = pd.DataFrame(columns = 
                    ["screen_name", "id", "desc", "creation_date",
                     "num_followers", "num_following", "num_tweets"])


user_dict = get_users()
data2 = pd.DataFrame.from_dict(user_dict,orient="index", columns =  ["partei"])

data = data.append(data2)
data = data.reset_index()
data.rename(columns = {"index":"name_id"}, inplace = True)
# %%
#run trough every mdb

for i in range(len(data.index)):

    
    username = data["name_id"][i]
    partei = data["partei"][i]
    try:
        target = api.get_user(id = username)
    except:
        print(username)
        continue
    
    #some general info about the user
    name = target.name
    creation_date = target.created_at
    desc = target.description
    id = target.id
    name = target.name
    num_followers = target.followers_count
    num_following = target.friends_count
    num_tweets = target.statuses_count

    #add data to dataframe
    data.iloc[i] = [username, name, id, desc, creation_date,
                    num_followers, num_following,num_tweets, partei]

#%%
data.to_csv("data/accounts_data.csv")
data["name_id"].values.to_csv("data/ids.csv")
#%%