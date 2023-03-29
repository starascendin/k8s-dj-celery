from config import celery_app
import snoop
import logging
import pandas as pd
from datetime import datetime, timedelta
from aininjas.tweetscrape.models import TweetDailySnap
from scripts.snscrape_twitter import main
from scripts.tweet_advertools import clean_string, is_thread, get_thread, main as adv_main

logger = logging.getLogger(__name__)

@celery_app.task(name="tweetscrape.task_daily_snap")
def task_daily_snap():
    # all_tweets, query = main()
    df = adv_main()
    query = ""
    all_tweets = df.to_string(index=False)
    tweetsnap = TweetDailySnap.objects.create(
        query_params=query,
        daily_snap='\n'.join(all_tweets)
    )
    
    return 'SUCCESS: task_daily_snap executed'
    
    