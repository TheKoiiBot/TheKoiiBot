import logging
from gemini import GeminiClient
from scheduler import TweetScheduler
from dashboard import Dashboard
from twitter_web import TwitterWebClient
import threading
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_timestamp(dt):
    if isinstance(dt, str):
        return dt
    return dt.strftime('%Y-%m-%d %H:%M:%S')

dashboard = None  # Global reference for dashboard

def log_tweet_to_dashboard(dashboard, tweet_text, timestamp):
    if dashboard:
        dashboard.queue.put(("tweet_success", {"timestamp": timestamp, "text": tweet_text}))
        print(f"[INFO] Tweet added to dashboard at {timestamp}")

def handle_successful_post(dashboard, result):
    log_tweet_to_dashboard(dashboard, result['text'], result['timestamp'])

class KoiiBot:
    def __init__(self, dashboard=None):
        self.gemini_client = GeminiClient()
        self.twitter_web_client = TwitterWebClient()
        self.scheduler = TweetScheduler(self.post_tweet)
        self.dashboard = dashboard
        self.running = False
    
    def post_tweet(self, tweet_text=None):
        try:
            if tweet_text is None:
                tweet_text = self.gemini_client.generate_tweet()
            logger.info(f"Generated tweet: {tweet_text}")
            result = self.twitter_web_client.post_tweet_web(tweet_text)
            logger.info(f"Tweet posted via web automation.")
            handle_successful_post(self.dashboard, result)
            return {'timestamp': result['timestamp'], 'text': result['text']}
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            if self.dashboard:
                self.dashboard.set_status("Inactive")
            raise
    
    def start(self):
        try:
            self.scheduler.schedule_tweets()
            self.scheduler.start()
            self.running = True
            if self.dashboard:
                self.dashboard.set_status("Active")
            logger.info("KoiiBot started successfully")
        except Exception as e:
            logger.error(f"Error starting KoiiBot: {str(e)}")
            if self.dashboard:
                self.dashboard.set_status("Inactive")
    
    def stop(self):
        self.scheduler.stop()
        self.running = False
        if self.dashboard:
            self.dashboard.set_status("Inactive")
        logger.info("KoiiBot stopped")

def run_initial_tweet(bot, dashboard):
    """Post an immediate tweet at startup and log it to the dashboard."""
    try:
        result = bot.post_tweet()
        logger.info("Initial startup tweet posted successfully.")
    except Exception as e:
        logger.error(f"Error posting initial startup tweet: {str(e)}")

def run_bot_with_dashboard():
    global dashboard
    dashboard = Dashboard()
    dashboard.set_status("Active")
    dashboard.schedule_daily_reset()

    def bot_thread():
        bot = KoiiBot(dashboard=dashboard)
        run_initial_tweet(bot, dashboard)
        bot.start()

    t_bot = threading.Thread(target=bot_thread, daemon=True)
    t_bot.start()

    # Start the dashboard UI in the main thread
    dashboard.mainloop()

def main():
    run_bot_with_dashboard()

if __name__ == "__main__":
    main()

# De main() functie moet weer als enige entrypoint actief zijn 