#%%
import tweepy 
import pandas as pd
import numpy as np
import configparser
import json
#%%
#authenticate with the twitter API using ini File
config = configparser.ConfigParser()		
config.read("config.ini")

keys = config["Twitter"]

consumer_key = keys["con_key"]
consumer_secret = keys["con_secret"]


auth = tweepy.AppAuthHandler(consumer_key,consumer_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
Cursor = tweepy.Cursor

#%%
df = pd.read_csv("data/ids.csv")
df = df.drop(columns = "Unnamed: 0")

#%%
#get the last tweets of the mdbs

def tweet_getter(list_of_ids, count = 20 ):
    """
    get the last tweets for the desired list of ids,
    additional argument = count, standard is 20 tweets
     """
    tweet_list = []

    for i in range(len(list_if_ids)):
        u_id = list_of_ids[i]
        user_tweets = api.user_timeline(
            u_id, count = count, tweet_mode = "extended", exclude_replies = False, include_rts = True
            )

        tweet_list.append(user_tweets)

    return tweet_list
        

#%%

id_list = df.name_id
#caution: tweet_getter return has to be the same length as the tweets column
df["tweets"] = tweet_getter(id_list)

#this returns an incredibly large JSON, 
#we want to extract the tweet text and possibly other metadata
#%%
#build the central dataframe for all tweet data
tweet_df = pd.DataFrame(columns = 
    ["user","t_text", "t_id", "t_date", "t_hashtags", "t_isrt", "t_isrpl", "other_users"]
)
#%%
#build functions to extract tweet data
def entitier(entity, typus):
    """ helper function for tweet_check(), input = entity dict 
    and a entity type, supported : "hashtags" and "users" """
    if len(entity) == 0:
        return None
    
    ents = []
    for i in entity:

        #there are different dictionarys depending on the selected entity
        if typus == "hashtags":
            extracted = i["text"]

        elif typus == "users":
            extracted = i["screen_name"]
        else:
            raise Exception("not a valid type of entity")

        ents.append(extracted)

    return ents


def tweet_check(status):
    """
    this function extracts some helpful data about a tweet, 
    input is a tweepy tweet object with related json 
     """
    t = status

    #check if it is a retweet, call of status throws exception if it isnt
    try:
        rt = t.retweeted_status
        t_isrt = True
    except:
        t_isrt = False

    #if it is a retweet, it is often truncated,
    # so we need to fetch the original tweet and extract data from there
    if t_isrt:
        t_text = t.retweeted_status.full_text
        hashtags_dict = t.retweeted_status.entities["hashtags"]

    else:
        t_text = t.full_text
        hashtags_dict = t.entities["hashtags"]



    #checks if it is a reply, call to stats_id returns None if it isnt a reply
    if type(t.in_reply_to_status_id) == type(None):
        t_isrpl = False
    else:
        t_isrpl = True

    #some general info about tweet
    user = t.user.screen_name
    t_id = t.id
    t_date = t.created_at
    other_u_dict = t.entities["user_mentions"]

    #the hashtags and other users return a list of dictionarys, which coulb be len 0,
    #so we define another function to check and extract the data
    other_users = entitier(other_u_dict, "users")
    t_hashtags = entitier(hashtags_dict, "hashtags")

    
    return {
        "user": user, "t_text": t_text, "t_id": t_id, 
        "t_date": t_date, "t_hashtags": t_hashtags, 
        "t_isrt": t_isrt, "t_isrpl": t_isrpl, "other_users": other_users
    }


def tweet_parser(list_of_status_objs):
    """ 
    extracts the data for all the tweet objects in the list,
    returns a central  dataframe 
    """
    tweet_df = pd.DataFrame(columns = 
        ["user","t_text", "t_id", "t_date", "t_hashtags",
         "t_isrt", "t_isrpl", "other_users"]
    )
    for status in list_of_status_objs:
        dic = tweet_check(status)
        tweet_df = tweet_df.append(dic, ignore_index=True)

    return tweet_df



#%%

# %%

