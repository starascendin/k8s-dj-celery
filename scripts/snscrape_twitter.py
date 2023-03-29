import snscrape.modules.twitter as sntwitter
import re
import pandas as pd
import json
from datetime import datetime, timedelta
# import emoji
### Create a client to access Twitter API



tweets = []
limit = 100


import tweepy
from typing import List, Dict

class TwitterScrapeClient:
    # def __init__(self, query='chatgpt', limit=100):
    #     pass
    
    # def search(self, query: str, count: int = 100, ) -> List[Dict[str, str, str, str]]:
    def search(self, query, count=100, filter=True):
        tweets_list = []
        results = sntwitter.TwitterSearchScraper(query=query)
        for i, tweet in enumerate(results.get_items()):
            print(f"{i} {tweet.url}")
            if len(tweets_list) > count:
                break
            if filter:
                # tweet.rawContent = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet.rawContent).split()).lower()
                tweet.rawContent = self.clean_string(tweet.rawContent.lower())
                ignore_keywords = ['web3', 'nft', 'metaverse', 'crypto', 'token', 'ido', 'airdrop', '🚀', 'btc', 'eth', 'decentralize', 'giveaway', 'erc20', '$']
                ## skip if ignore words
                if any(word in tweet.rawContent for word in ignore_keywords):
                    continue
                ## thread content if applicable
                thread_keywords = ['1/', 'thread', 'a thread', '🧵']
                if any(word in tweet.rawContent for word in thread_keywords):
                    tweet.rawContent = self.get_thread(thread_id=tweet.id)
                    tweet.rawContent = self.clean_string(tweet.rawContent.lower())
                    # print("####### Thread #####")
                    # print(tweet.rawContent)
                    # tweet.rawContent = '\n'.join(tweet_thread)
                    # tweets_list.append([tweet.date, tweet.id, tweet.rawContent, tweet.user.username])
                    tweets_list.append(tweet)
                elif len(tweet.rawContent) > 130:
                    # tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])
                    tweets_list.append(tweet)
            else:
                # tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])
                tweets_list.append(tweet)

        return tweets_list

    def clean_string(self, txt):
        pattern_list = [r"#(\w+)", r"@(\w+)",r"http\S+", r" +", "\n"]
        for p in pattern_list:
            txt = re.sub(p, ' ', txt, flags=re.MULTILINE)
        return txt

    # def _format_results(self, results, columns=None) -> None:
    #
    #         df = pd.DataFrame(tweets, columns=columns)
    #         return df
    def get_thread(self, thread_id, limit=50, filter=True):
        # https://github.com/JustAnotherArchivist/snscrape/issues/291
        client = sntwitter.TwitterTweetScraper(thread_id, mode=sntwitter.TwitterTweetScraperMode.SCROLL)
        threads = []
        counter = 0
        for tweet in client.get_items():
            # print(tweet)
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

    def get_specific_tweet(self, tweet_id):
        print(tweet_id)
        tweets_list = []
        # Using TwitterSearchScraper to scrape data and append tweets to list
    
        for tweet in sntwitter.TwitterTweetScraper(tweetId=tweet_id,mode=sntwitter.TwitterTweetScraperMode.SCROLL).get_items():
            # print(tweet)
            tweets_list.append(tweet)
            
        print(tweets_list)

def main():
    x = TwitterScrapeClient()
    # (#AI artificialintelligence) min_retweets:100 lang:en until:2023-01-31 since:2023-01-09 -filter:links
    topics = ['ai']#, 'artificialintelligence']
    topics = 'ai'
    min_tweets = 50
    # date_start = '2023-02-05'
    # date_end = '2023-02-08'
    date_start = (datetime.today()-timedelta(1)).strftime('%Y-%m-%d')
    date_end = datetime.today().strftime('%Y-%m-%d')

    # query = f"({' OR '.join(topics)}) min_retweets:{min_tweets} lang:en until:{date_end} since:{date_start}"
    query = f"{topics} min_retweets:{min_tweets} lang:en until:{date_end} since:{date_start}"
    results = x.search(query, filter=True, count=100)
    df = pd.DataFrame(results)
    df['username'] = [u['username'] for u in df.user]
    df = df[df.id == df.conversationId]
    df = df.loc[:,['url','date','rawContent','username','replyCount', 'retweetCount', 'likeCount','viewCount']]
    print('\n* '.join(df.rawContent))
    # tweets = []
    # for tweet in results.get_items():
    #     tweets.append(tweet)
    #     if len(tweets) >= limit:
    #         break
    all_tweets = []
    for t in results:
        print(len(t.rawContent))
        all_tweets.append(t.rawContent)


    # twt = x.get_specific_tweet('1615406451136073744')
    thread = x.get_thread('1615406451136073744')

    # df = x._format_results(tweets, columns=['id', 'date', 'content', 'user', 'replies', 'retweets', 'likes', 'url'])


    # print(df)
    print("#done")
    return [all_tweets, query]
    

if __name__ == '__main__':
    main()
