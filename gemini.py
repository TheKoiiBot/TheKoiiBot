import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import re

class GeminiClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_tweet(self) -> str:
        """
        Generate a tweet about the KOII project using Gemini AI.
        Returns a string containing the generated tweet.
        """
        fallback_tweet = "KOII is revolutionizing digital ownership. Discover more at https://www.koii.network/ #KOII"
        for attempt in range(3):
            try:
                prompt = (
                    "Write a helpful, unique, and self-contained tweet in English about the KOII ecosystem. "
                    "The tweet must mention $KOII somewhere in the text. "
                    "Do NOT include any links, URLs, or bracketed/placeholder text. "
                    "Only provide concise, informative, and complete information about KOII. "
                    "Never repeat phrasing or content. Each tweet must start differently than previous ones. "
                    "Use varied sentence structures and wording. Max 280 characters."
                )
                response = self.model.generate_content(prompt)
                tweet = response.text.strip() if response.text else ''
                # Remove any bracketed or parenthetical text (e.g., [ ... ] or ( ... ))
                tweet = re.sub(r'\[.*?\]', '', tweet)
                tweet = re.sub(r'\(.*?\)', '', tweet)
                tweet = tweet.strip()
                # Try to avoid abrupt cut-off by trimming to last full sentence if too long
                if len(tweet) > 280:
                    logging.warning(f"[Gemini] Tweet too long ({len(tweet)} chars), trimming to 280.")
                    trimmed = tweet[:280]
                    if '.' in trimmed:
                        tweet = trimmed[:trimmed.rfind('.')+1].strip()
                    else:
                        tweet = trimmed.strip()
                if not tweet:
                    logging.error(f"[Gemini] Empty response on attempt {attempt+1}.")
                    continue
                return tweet
            except Exception as e:
                logging.error(f"[Gemini] Error generating tweet (attempt {attempt+1}): {str(e)}")
        logging.error("[Gemini] All attempts failed, using fallback tweet.")
        return fallback_tweet

if __name__ == "__main__":
    client = GeminiClient()
    try:
        tweet = client.generate_tweet()
        print(f"Generated tweet: {tweet}")
        print(f"Tweet length: {len(tweet)} characters")
    except Exception as e:
        print(f"Error: {str(e)}") 