import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TweetScheduler:
    def __init__(self, tweet_callback):
        """
        Initialize the scheduler with a callback function that will be called
        when it's time to post a tweet.
        
        Args:
            tweet_callback: Function to call when it's time to post a tweet
        """
        self.scheduler = BackgroundScheduler()
        self.tweet_callback = tweet_callback
        
    def schedule_tweets(self):
        """Schedule a tweet every 2 hours on the hour."""
        self.scheduler.add_job(
            self.tweet_callback,
            CronTrigger(minute=0, hour='*/2'),  # Every 2 hours at minute 0
            id='bi_hourly_tweet',
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        logger.info("Scheduled tweets: 1 per 2 hours, every 2 hours on the hour.")
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Tweet scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Tweet scheduler stopped")

if __name__ == "__main__":
    # Test the scheduler
    def test_callback():
        logger.info("Test callback executed")
    
    scheduler = TweetScheduler(test_callback)
    scheduler.schedule_tweets()
    scheduler.start()
    
    # Keep the script running for a while to test
    import time
    time.sleep(10)
    scheduler.stop() 