#%%
import tweepy 
import pandas as pd
import os
#from fetch import api_auth
import configparser 

#%%
#get every mdb and his party from  astored text file
def get_users_from_file(path_for_files = "/Users/code/Desktop/bundestag/partei/"):

    """ get the users located in the subdirectory in txt files
    with the name of the file being their party """

    dict = {}
    files = os.listdir(path_for_files)[1:]
    for parteifile in files:
        with open(path_for_files + parteifile) as f:
            for line in f:
                line =  line.strip("\n")
                dict[line] = parteifile[:-4]
    
    return dict

#get twitter data about a specified user
def get_user_info(username):
    """ Func to extract data from a given twitter username
    """
    try:
        target = api.get_user(id = username)
    except:
        return print("failed:" + username)
    
    #some general info about the user
    name = target.name
    creation_date = target.created_at
    desc = target.description
    id = target.id
    num_followers = target.followers_count
    num_following = target.friends_count
    num_tweets = target.statuses_count

    return {"username": username,
        "name":name, "created_at":creation_date, "desc":desc, "u_id": id,
        "num_followers":num_followers, "num_following":num_following, 
        "num_tweets": num_tweets
    }

#get a table for twitter data from inputted users
def user_list(dictionary):
    """ takes as input a list of usernames and their party affiliation,
        returns a dataframe with info about twitter accounts extracted
     """

    central_df = pd.DataFrame(
        columns = ["username", 'name', 'created_at', 'desc', 'u_id', 'num_followers', 'num_following',
       'num_tweets', "partei"]
    )

    for user, partei in dictionary.items():
        extracted = get_user_info(user)
        central_df = central_df.append(extracted, ignore_index = True)
        central_df.partei[-1:] = partei
    return central_df


#%%
#api = api_auth()

user_dict = get_users_from_file()
df = user_list(user_dict)

#%%
data.to_csv("data/accounts_data.csv")

#data["name_id"].values.to_csv("data/ids.csv")
#%%

config = configparser.ConfigParser()		
config.read("config.ini")
keys = config["Twitter"]

consumer_key = keys["con_key"]
consumer_secret = keys["con_secret"]

app_auth = tweepy.AppAuthHandler(consumer_key,consumer_secret)

api = tweepy.API(app_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
# %%
