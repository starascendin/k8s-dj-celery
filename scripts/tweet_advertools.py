import pandas as pd
import numpy as np
import advertools as adv
import os.path as path
import re
import snscrape.modules.twitter as sntwitter
from datetime import datetime


import warnings
def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()


auth_params = {
'app_key': 'RQOGhTNFC1msCHEtWITEzrnZA',
'app_secret': 'x5nYtrdfRMD6hejs6wOU784ZQgfwQD6SSEVJRgHOijyhmhaPf9',
'oauth_token': '1543780298357293056-cP5KzlvpTdWmGJGAds3Q5x96FlEW16',
'oauth_token_secret': 'vxAGhbtTB0j8GA7FSzErddXPwJBFKmMOrtcWnVwZ1i6HY',
}
adv.twitter.set_auth_params(**auth_params)

AI_LIST = 1633404466602082304

# home_timeline = adv.twitter.get_home_timeline(tweet_mode='extended')
# print(home_timeline.shape)
# home_timeline.head(3)

def clean_string(txt):
    pattern_list = [r"#(\w+)", r"@(\w+)", r"http\S+", r" +", "\n"]
    for p in pattern_list:
        txt = re.sub(p, ' ', txt, flags=re.MULTILINE)
    return txt

def is_thread(id):
    client = sntwitter.TwitterTweetScraper(id, mode=sntwitter.TwitterTweetScraperMode.SCROLL)
    thread = []
    counter = 0
    for tweet in client.get_items():
        thread.append(tweet)
        counter += 1
        if counter > 1:
            break
    if len(thread) < 2:
        return False
    rsp = False
    if thread[0].user.username == thread[1].user.username:
        rsp = True
    return rsp

def get_thread(thread_id, limit=30, filter=True):
    # https://github.com/JustAnotherArchivist/snscrape/issues/291
    client = sntwitter.TwitterTweetScraper(thread_id, mode=sntwitter.TwitterTweetScraperMode.SCROLL)

    thread = []
    counter = 0
    for tweet in client.get_items():
        thread.append(tweet)
        counter += 1
        if counter > limit:
            break
    filtered_thread = []
    if filter:
        for tweet in thread:
            if tweet.user.username == thread[0].user.username and tweet.rawContent[0] != '@':
                filtered_thread.append(tweet.rawContent)
    if len(filtered_thread) > 1:
        out_text = ' '.join(filtered_thread)
    else:
        out_text = filtered_thread[0]
    return out_text

def filterTweet(t):
    ## If it's a retweet, fetch the original tweet
    if t['tweet_full_text'][0:2] == 'RT':
        t = adv.twitter.lookup_status(id=t['tweet_retweeted_status']['id'], tweet_mode="extended").squeeze(axis=0)
    t['tweet_full_text'] = clean_string(t['tweet_full_text'].lower())
    # ignore_keywords = ['web3', 'nft', 'metaverse', 'crypto', 'token', 'ido', 'airdrop', '🚀', 'btc', 'eth',
    #                    'decentralize', 'giveaway', 'erc20', '$']
    ignore_keywords = []

    ## skip if ignore words
    if any(word in t['tweet_full_text'] for word in ignore_keywords):
        return None
    ## thread content if applicable
    # thread_keywords = ['1/', 'thread', 'a thread', '🧵']
    # if any(word in t['tweet_full_text'] for word in thread_keywords):
    #     t['tweet_full_text'] = get_thread(thread_id=t['tweet_id'])
    #     t['tweet_full_text'] = clean_string(t['tweet_full_text'].lower())
    #     return t
    ## treat every post as a potential thread
    if is_thread(id=t['tweet_id']):
        t['tweet_full_text'] = get_thread(thread_id=t['tweet_id'])
        t['tweet_full_text'] = clean_string(t['tweet_full_text'].lower())
        return t
    if len(t['tweet_full_text']) > 150:
        return t
    return None




# if path.exists("tweet_list_db.csv"):
#     df = pd.read_csv("tweet_list_db.csv")
# else:
#     df = pd.DataFrame(columns=['date','id', 'text'])

# data = []
# list_statuses = adv.twitter.get_list_statuses(list_id=AI_LIST, tweet_mode='extended', include_rts=True)
# for i in range(list_statuses.shape[0]):
#     print(i)
#     t = list_statuses.iloc[i,:]
#     tweet = filterTweet(t)
#     if tweet is not None:
#         data.append([
#             tweet['tweet_id'],
#             tweet['tweet_full_text']
#         ])

# df = pd.DataFrame(data)
# df.columns = ['id', 'text']
# df['datetime'] = datetime.now().date()
# df.to_csv('tweet_list_db.csv', index=False)

## Access tweet by ID
# https://twitter.com/anyuser/status/<tweet_id>
# t = adv.twitter.lookup_status(id=1635452269264248832, tweet_mode="extended").squeeze(axis=0)
def main():

    if path.exists("tweet_list_db.csv"):
        df = pd.read_csv("tweet_list_db.csv")
    else:
        df = pd.DataFrame(columns=['date','id', 'text'])

    data = []
    list_statuses = adv.twitter.get_list_statuses(list_id=AI_LIST, tweet_mode='extended', include_rts=True)
    for i in range(list_statuses.shape[0]):
        print(i)
        t = list_statuses.iloc[i,:]
        tweet = filterTweet(t)
        if tweet is not None:
            data.append([
                tweet['tweet_id'],
                tweet['tweet_full_text']
            ])

    df = pd.DataFrame(data)
    df.columns = ['id', 'text']
    df['datetime'] = datetime.now().date()
    # df.to_csv('tweet_list_db.csv', index=False)
    return df
    
if __name__ == "__main__":
    df = main()
    all_tweets = df.to_string(index=False)
    print("#all ", all_tweets)
    df.to_csv('tweet_list_db.csv', index=False)