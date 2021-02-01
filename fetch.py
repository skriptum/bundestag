import tweepy 
import pandas as pd
import numpy as np

consumer_key = "zLhaEr6YbhAyUJDKykXt7rShh"

consumer_secret = "A8WoN8CERsebjyGAvTAVCDiDtixB5mQenvuszFxQ2A3YF4yc2Q"


auth = tweepy.AppAuthHandler(consumer_key,consumer_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
Cursor = tweepy.Cursor

#%%
df = pd.read_csv("partei/ids")


#%%
#get the last tweets of the mdbs
df["tweets"] = None
for i in range(len(df.name_id)):
    u_id = df.name_id[i]
    count = 50 
    tweets = api.user_timeline(u_id, count = count, tweet_mode = "extended", exclude_replies = True)
    df["tweets"][i] = tweets

#this returns an incredibly large JSON, 
#we want to extract the tweet text and possibly other metadata
#%%
# df["data"] = 0


# for i in range(len(df.index)):
#     dic = {}
#     tweets= df.tweets[0]
#     for t in tweets:
#         t_id = t.id
#         full_text = t.full_text
#         date = t.created_at
#         if "RT" in full_text:
#             rt = True
#         else:
#             rt = False
#         dic["t_id"] = 
        
        
# try:
#     for im in t.extended_entities["media"]:
#         im_url = im["media_url_https"]
# except:
#     im_url = False
            
        
#%%
df["text"] = 0
for i  in range(len(df.index)):
    text = []
    tweets = df["tweets"][i]
    for t in tweets:
        full_text = t.full_text
        text.append(full_text)
    df["text"][i] = text
    
df.to_csv("texte")
#this is huge (~500MB)