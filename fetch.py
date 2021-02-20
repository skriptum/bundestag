#%%
import tweepy 
import pandas as pd
import numpy as np
import configparser
import json
import datetime
import os
from textblob_de import TextBlobDE as TextBlob

#%%
print("starting function and authorizing")
#function for auth with api
def api_auth(config_file = "config.ini"):
    """ authenticates with the twitter api, returns api
    """
    config = configparser.ConfigParser()		
    config.read(config_file)
    keys = config["Twitter"]

    consumer_key = keys["con_key"]
    consumer_secret = keys["con_secret"]

    app_auth = tweepy.AppAuthHandler(consumer_key,consumer_secret)

    interface = tweepy.API(app_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return interface

api = api_auth()
#%%
#functions to get user data

#get users from files
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
        print("failed:" + username)
        return {"name_id": username}
    
    #some general info about the user
    name = target.name
    creation_date = target.created_at
    desc = target.description
    id = target.id
    num_followers = target.followers_count
    num_following = target.friends_count
    num_tweets = target.statuses_count
    image = target.profile_image_url.replace("_normal", "") 

    return {"name_id": username,
        "name":name, "created_at":creation_date, "desc":desc, "u_id": id,
        "num_followers":num_followers, "num_following":num_following, 
        "num_tweets": num_tweets, "img": image,
    }

#get a table for twitter data from inputted users
def user_list(dictionary):
    """ takes as input a list of usernames and their party affiliation,
        returns a dataframe with info about twitter accounts extracted
     """

    central_df = pd.DataFrame(
        columns = ["name_id", 'name', 'created_at', 'desc', 'u_id', 'num_followers', 'num_following',
       'num_tweets',"img", "partei"]
    )

    for user, partei in dictionary.items():
        extracted = get_user_info(user)
        extracted["partei"] = partei
        central_df = central_df.append(extracted, ignore_index = True)
    return central_df


#%%
#Functions to ge tweet data

#function to get 20 tweets from the given ids
def tweet_getter(list_of_ids, count = 20 ):
    """
    get the last tweets for the desired list of ids,
    additional argument = count, standard is 20 tweets
     """
    tweet_list = []

    for i in range(len(list_of_ids)):
        u_id = list_of_ids[i]
        try:
            user_tweets = api.user_timeline(
                u_id, count = count, tweet_mode = "extended", exclude_replies = False, include_rts = True
                )

            tweet_list.append(user_tweets)
        except:
            print(u_id)
            continue

    return tweet_list


#helper function for data extracter
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


#function to extract the data of a tweet object/json
def tweet_check(status):
    """
    this function extracts some helpful data about a tweet, 
    input is a tweepy tweet object with related json 
     """
    t = status
    if type(t) is not tweepy.models.Status:
        raise Exception("Not a status object")

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
        "name_id": user, "t_text": t_text, "t_id": t_id, 
        "t_date": t_date, "t_hashtags": t_hashtags, 
        "t_isrt": t_isrt, "t_isrpl": t_isrpl, "other_users": other_users
    }


#function to parse all data of a list of status and put it in a dataframe
def tweet_parser(list_of_status_objs):
    """ 
    extracts the data for all the tweets in the list,
    returns a central  dataframe 
    """
    tweet_df = pd.DataFrame(columns = 
        ["name_id","t_text", "t_id", "t_date", "t_hashtags",
         "t_isrt", "t_isrpl", "other_users"]
    )
    for status in list_of_status_objs:
        dic = tweet_check(status)
        tweet_df = tweet_df.append(dic, ignore_index=True)

    return tweet_df


#metrication of a users tweets dataframe
def metricate(tweetdf):
    """ takes a dataframe with tweets from
     one user and calculates some metrics for it.
     returns these values as dict
    """
    if len(tweetdf) == 0:
        return None

    user = tweetdf.name_id[0]
    #percent of retweets and replies of total tweets
    retweet_rate = tweetdf.t_isrt.mean()
    replie_rate =  tweetdf.t_isrpl.mean()

    #now i want the tweets per day
    ix = len(tweetdf.index) -1
    last_tweet = tweetdf.t_date[ix].to_pydatetime()
    td = datetime.datetime.now() - last_tweet

    days = td.total_seconds() / (3600*24)
    ts_perday = len(tweetdf) / days

    #hashtags
    hs = ""
    hashtags = tweetdf.t_hashtags
    hashtags = hashtags.explode().dropna()
    for h in hashtags:
        hs += h + ", "

    #sentiment analysis (experimental)
    sentiments = []
    for text in tweetdf.t_text.values:
        blob = TextBlob(text)
        sent = blob.polarity
        sentiments.append(sent)
    avg_sent = np.mean(sentiments)

    return {"name_id": user,
        "retweet_rate": retweet_rate, "replie_rate": replie_rate,
        "ts_perday": ts_perday, "hashtags":hs, "avg_sent": avg_sent
    }



#%%
#lets do this part1, get all users

user_dict = get_users_from_file() #get the users from the files


df = user_list(user_dict)  #get the dataframe with user data

id_list = df.name_id #built the list of ids
id_list = id_list.values 

#%%

#part2 get all tweets
tweet_json = tweet_getter(id_list) #gets the json files for all the tweets


#build the dataframe for user metrics
metric_df = pd.DataFrame(columns = 
    ["name_id", "retweet_rate", "replie_rate", "ts_perday", "hashtags", "avg_sent"]
    )


#get user metrics for all users
for obj in tweet_json:
    t_df = tweet_parser(obj) #should i store all tweets somewhere ? !!
    metrics = metricate(t_df)
    metric_df = metric_df.append(metrics, ignore_index = True)

# add @ in front of every name in metric_df
metric_df["name_id"] = "@"+ metric_df.name_id

#merge both dataframes
a_df = pd.merge(df, metric_df, how = "left", on = "name_id")

#calculate tweet_rate ( if it is not a retweet or a replie)
a_df["tweet_rate"] = 1 - (a_df.retweet_rate + a_df.replie_rate)
a_df["img"] = a_df["img"].str.replace("http://", "https://")


a_df.to_csv("dash/data/accounts_data.csv")
