import tweepy
import psycopg2
import pandas as pd
import os.path as path
import re
import snscrape.modules.twitter as sntwitter

# Twitter API credentials
consumer_key = 'RQOGhTNFC1msCHEtWITEzrnZA'
consumer_secret = 'x5nYtrdfRMD6hejs6wOU784ZQgfwQD6SSEVJRgHOijyhmhaPf9'
access_token = '1543780298357293056-cP5KzlvpTdWmGJGAds3Q5x96FlEW16'
access_secret = 'vxAGhbtTB0j8GA7FSzErddXPwJBFKmMOrtcWnVwZ1i6HY'
bearer = "AAAAAAAAAAAAAAAAAAAAAHeelAEAAAAAm%2Fqmkkuiz0dAg24DKG8ztkPV6wI%3DUmXBoDDCsymP21ChCWMnjOkXebyKrRhkrSnHJ2XszAACx3Qoiu"

client_secret_v2 = '2kr2kbxwJN-GXoh2t5a4JybF2NcQqDbLm1r43gdeCfiJNp_9ir'

# 3TMALck4TyH18uiBl40h9pEjZ
# 8Ubc9gbJVLt7QCYazLySUuNGOx2AbaJiOUTrCtVF7J4aXB5wqi
# AAAAAAAAAAAAAAAAAAAAAHeelAEAAAAALdLytMdJP8gbhIY%2BBG2AraP309c%3D4pY99Qrl7jlJjfFXhBWepa1ZiaArGfomPuYSEoff5ibtqWQZyV

# Connect to Twitter API
try:
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
except Exception as e:
    print(f"Error connecting to Twitter API: {e}")
    exit(1)

if path.exists("personal_thread_DB.csv"):
    df = pd.read_csv("personal_thread_DB.csv")
else:
    df = pd.DataFrame(columns=['id', 'text', 'user', 'user_id'])


def clean_string(txt):
    pattern_list = [r"#(\w+)", r"@(\w+)", r"http\S+", r" +", "\n"]
    for p in pattern_list:
        txt = re.sub(p, ' ', txt, flags=re.MULTILINE)
    return txt

def get_thread(thread_id, limit=50, filter=True):
    # https://github.com/JustAnotherArchivist/snscrape/issues/291
    client = sntwitter.TwitterTweetScraper(thread_id, mode=sntwitter.TwitterTweetScraperMode.SCROLL)
    threads = []
    counter = 0
    for tweet in client.get_items():
        threads.append(tweet)
        counter += 1
        if counter > limit:
            break
    filtered_thread = []
    if filter:
        for tweet in threads:
            if tweet.user.username == threads[0].user.username and tweet.rawContent[0] != '@':
                filtered_thread.append(tweet.rawContent)
    if len(filtered_thread) > 1:
        out_text = ' '.join(filtered_thread)
    else:
        out_text = filtered_thread[0]
    return out_text

def filterTweet(t):
    # tweet.rawContent = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet.rawContent).split()).lower()
    t['full_text'] = clean_string(t['full_text'].lower())
    # ignore_keywords = ['web3', 'nft', 'metaverse', 'crypto', 'token', 'ido', 'airdrop', '🚀', 'btc', 'eth',
    #                    'decentralize', 'giveaway', 'erc20', '$']
    ignore_keywords = []

    ## skip if ignore words
    if any(word in t['full_text'] for word in ignore_keywords):
        return None
    ## thread content if applicable
    thread_keywords = ['1/', 'thread', 'a thread', '🧵']
    if any(word in t['full_text'] for word in thread_keywords):
        t['full_text'] = get_thread(thread_id=t['id'])
        t['full_text'] = clean_string(t['full_text'].lower())
        return t
    elif len(t['full_text']) > 130:
        return t
    return None

following = api.get_friend_ids()
data = []
for f in following:
    print(f"Working on {f}")
    try: # if there is a previous entry from this user
        last_id = max(df.loc[df.user_id == f, 'id'])
        tweets = api.user_timeline(user_id=f, since_id=last_id, include_rts=True, tweet_mode="extended")
    except: # else scrape 30 messages from user
        tweets = api.user_timeline(user_id=f, count=30, include_rts=True, tweet_mode="extended")
    for tweet in tweets:
        tweet = tweet._json
        tweet = filterTweet(tweet)
        if tweet != None:
            data.append([tweet['id'],tweet['full_text'], tweet['user']['screen_name'], tweet['user']['id']])

df_new = pd.DataFrame(data)
df_new.columns = df.columns
df_new.to_csv("personal_thread_DB.csv")




# if __name__ == '__main__':

    # ## testing
    # t = api.get_status('1627572547276492800')
    # url = f"https://twitter.com/i/web/status/{'1627572543023357953'}"

    # def get_specific_tweet(tweet_id):
    #     print(tweet_id)
    #     tweets_list = []
    #     for tweet in sntwitter.TwitterTweetScraper(tweetId=tweet_id,
    #                                             mode=sntwitter.TwitterTweetScraperMode.SCROLL).get_items():
    #         # print(tweet)
    #         tweets_list.append(tweet)
    #     return tweets_list
    # t2 = get_specific_tweet('1627572543023357953')
    # t2 = get_specific_tweet('1627572547276492800')