import os
import tweepy
from dotenv import load_dotenv

class TwitterClient:
    def __init__(self):
        load_dotenv()
        
        # Load Twitter API credentials
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        
        # Validate credentials
        if not all([api_key, api_secret, access_token, access_secret]):
            raise ValueError("Missing Twitter API credentials in environment variables")
        
        # Initialize Twitter API client
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth)
        
        # Verify credentials
        try:
            self.api.verify_credentials()
        except Exception as e:
            raise Exception(f"Failed to verify Twitter credentials: {str(e)}")

    def post_tweet(self, tweet_text: str) -> dict:
        """
        Post a tweet using the Twitter API.
        Returns a dictionary with the tweet details.
        """
        try:
            # Post the tweet
            tweet = self.api.update_status(tweet_text)
            
            # Return tweet details
            return {
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'url': f"https://twitter.com/user/status/{tweet.id}"
            }
            
        except Exception as e:
            raise Exception(f"Error posting tweet: {str(e)}")

if __name__ == "__main__":
    # Test the tweet posting
    client = TwitterClient()
    try:
        result = client.post_tweet("Test tweet from KoiiBot!")
        print(f"Tweet posted successfully: {result['url']}")
    except Exception as e:
        print(f"Error: {str(e)}") 