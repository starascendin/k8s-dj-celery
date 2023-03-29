import tweepy
from typing import List, Dict

class TwitterClient:
    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str, bearer_token=None):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth)
        self.client = tweepy.Client(
            bearer_token=bearer_token, consumer_key=consumer_secret, consumer_secret=consumer_secret, access_token=access_token, access_token_secret=access_token_secret
            )
        self.thread_tweets: List[str] = []
    
    ## search by topic
    def search(self, topic: str, count: int = 100) -> List[Dict[str, str]]:
        # Define search term and number of tweets
        search_term = topic
        number_of_tweets = count

        # Search for tweets
        tweets = tweepy.Cursor(self.api.search_tweets, q=search_term, count=100, result_type='popular', include_entities=True, lang='en').items(number_of_tweets)
        return tweets


    def create_thread(self, thread_content: List[Dict[str, str]]) -> None:
        """
        Create a twitter thread
        thread_content : list
            list of dictionaries each containing 'content' key and an optional 'video_file' key
        """
        if not all(map(lambda x: isinstance(x, dict) and 'content' in x, thread_content)):
            raise ValueError("thread_content must be a list of dictionaries with 'content' key")

        for tweet_data in thread_content:
            if 'video_file' in tweet_data:
                if not isinstance(tweet_data['video_file'], str):
                    raise ValueError("'video_file' must be a string")
                media_ids = [self.api.media_upload(tweet_data['video_file']).media_id]
            else:
                media_ids = None
            if self.thread_tweets:
                new_tweet = self.api.update_status(tweet_data['content'], in_reply_to_status_id=self.thread_tweets[-1], media_ids=media_ids)
            else:
                new_tweet = self.api.update_status(tweet_data['content'], media_ids=media_ids)
            self.thread_tweets.append(new_tweet.id)


if __name__ == '__main__':
    # Create a TwitterClient object
    client = TwitterClient('MFWVSHu5EIUf5atp6dPU6bQE3', 'LNr9qQeMQlT4ZZTeUWCuJlxpBurfOh6AiYyl3i3CL6X56k8odi', '1442144132290338817-QA2fwfCTPmhw7W8H9BoBfqmuNP4MnU', 'noJqhE09x7NKqjWk9B2VsMXniNk0das00edKC51MvZqOD', bearer_token="AAAAAAAAAAAAAAAAAAAAAN5%2BlAEAAAAAKEwJsUc7BcxbEfqqecR0OdCWbjQ%3DGPZQXJmFnY1SB6ZT8IBhh6scjIexXWBzoX8GCUnJlvDjEHdvZY")
    # client = tweepy.Client("AAAAAAAAAAAAAAAAAAAAAN5%2BlAEAAAAAKEwJsUc7BcxbEfqqecR0OdCWbjQ%3DGPZQXJmFnY1SB6ZT8IBhh6scjIexXWBzoX8GCUnJlvDjEHdvZY")
    tweets = client.search('chatgpt')
    print("tweets: ", tweets)

    print("#### ")