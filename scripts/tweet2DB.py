import snscrape.modules.twitter as sntwitter

import pandas as pd
import json

### Create a client to access Twitter API


tweets = []
limit = 100

import tweepy
from typing import List, Dict


class TwitterScrapeClient:
    # def __init__(self, query='chatgpt', limit=100):
    #     pass

    def search(self, query: str, top: bool, count: int = 100) -> List[Dict[str, str]]:
        results = sntwitter.TwitterSearchScraper(query=query, top=top)

        return results

    def _format_results(self, results, columns=None) -> None:

        df = pd.DataFrame(tweets, columns=columns)
        return df

    def get_thread(self, thread_id):
        # https://github.com/JustAnotherArchivist/snscrape/issues/291
        client = sntwitter.TwitterTweetScraper(thread_id, mode=sntwitter.TwitterTweetScraperMode.SCROLL)
        threads = []
        for tweet in client.get_items():
            # print(tweet)
            threads.append(tweet)
        return threads

    def get_specific_tweet(self, tweet_id):
        print(tweet_id)
        tweets_list = []
        # Using TwitterSearchScraper to scrape data and append tweets to list

        for tweet in sntwitter.TwitterTweetScraper(tweetId=tweet_id,
                                                   mode=sntwitter.TwitterTweetScraperMode.SCROLL).get_items():
            print(tweet)
            tweets_list.append(tweet)

        print(tweets_list)


if __name__ == '__main__':
    x = TwitterScrapeClient()
    # results = x.search('AI', top=True)
    results = x.search('AI%20min_faves%3A1000', top=True)
    tweets = []
    for tweet in results.get_items():
        tweets.append(tweet)
        if len(tweets) >= limit:
            break

    df = pd.DataFrame(tweets)

    # twt = x.get_specific_tweet('1615406451136073744')
    thread = x.get_thread('1615406451136073744')

    # df = x._format_results(tweets, columns=['id', 'date', 'content', 'user', 'replies', 'retweets', 'likes', 'url'])

    # print(df)
    print("#done")