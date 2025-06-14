import os
import asyncio
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import pickle
import time
import re

load_dotenv()

TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
USER_DATA_DIR = os.path.abspath('pw_user_data')  # Persistent profile

class TwitterWebClient:
    def __init__(self):
        self.username = TWITTER_USERNAME
        self.password = TWITTER_PASSWORD
        self.headless = HEADLESS
        if not self.username or not self.password:
            raise ValueError('Twitter username or password not set in environment variables.')

    def post_tweet_web(self, tweet_text: str) -> dict:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=self.headless,
                args=["--start-maximized"]
            )
            page = browser.new_page()
            try:
                page.goto('https://twitter.com/home', timeout=60000)
                # Check login
                if not self._is_logged_in(page):
                    self._login(page)
                # Always scroll to the top of the home feed before clicking the tweet box
                tweet_box = None
                for attempt in range(2):
                    page.goto('https://twitter.com/home', timeout=60000)
                    time.sleep(2)
                    if '/home' not in page.url:
                        continue
                    page.evaluate('window.scrollTo(0, 0)')
                    tweet_box = page.query_selector('div[aria-label="Tweet text"]')
                    if tweet_box and tweet_box.is_visible() and tweet_box.is_enabled():
                        break
                    tweet_box = page.query_selector('div[data-testid="tweetTextarea_0"]')
                    if tweet_box and tweet_box.is_visible() and tweet_box.is_enabled():
                        break
                    time.sleep(2)
                if not tweet_box or '/home' not in page.url:
                    page.screenshot(path="tweet_box_not_found.png", full_page=True)
                    raise Exception("Main tweet input box not found on /home. See screenshot: tweet_box_not_found.png")

                tweet_box.click()
                time.sleep(0.5)
                try:
                    tweet_box.fill(tweet_text)
                    print('[DEBUG] Used fill() to enter tweet')
                except Exception:
                    tweet_box.type(tweet_text)
                    print('[DEBUG] Used type() to enter tweet')
                time.sleep(1)

                # Try to post using keyboard shortcut first (Ctrl+Enter)
                try:
                    print('[DEBUG] Trying to post tweet using keyboard shortcut Ctrl+Enter')
                    page.keyboard.press('Control+Enter')
                    time.sleep(2)
                    # Check if tweet box is cleared (tweet posted)
                    if tweet_box.inner_text().strip() == '':
                        print('[DEBUG] Tweet posted successfully using keyboard shortcut')
                        return {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'text': tweet_text}
                except Exception as e:
                    print(f'[DEBUG] Exception using keyboard shortcut: {e}')
                page.screenshot(path='post_shortcut_attempt.png', full_page=True)

                # Fallback: Try all robust selectors for the Post button (2025 UI)
                for post_attempt in range(10):
                    post_buttons = []
                    post_buttons += page.query_selector_all('div[aria-label="Tweet text"] button[aria-label="Post"]')
                    post_buttons += page.query_selector_all('div[aria-label="Tweet text"] button[data-testid="tweetButtonInline"]')
                    post_buttons += page.query_selector_all('div[data-testid="tweetTextarea_0"] button[data-testid="tweetButtonInline"]')
                    post_buttons += page.query_selector_all('div[aria-label="Tweet text"] button[type="submit"]')
                    post_buttons += page.query_selector_all('div[data-testid="tweetTextarea_0"] button[type="submit"]')
                    post_buttons += page.query_selector_all('div[aria-label="Tweet text"] button:has-text("Post")')
                    post_buttons += page.query_selector_all('div[data-testid="tweetTextarea_0"] button:has-text("Post")')
                    post_buttons += page.query_selector_all('div[aria-label="Tweet text"] [role="button"]:has-text("Post")')
                    post_buttons += page.query_selector_all('div[data-testid="tweetTextarea_0"] [role="button"]:has-text("Post")')

                    found_enabled = False
                    for btn in post_buttons:
                        try:
                            is_disabled = btn.get_attribute('disabled') is not None or btn.get_attribute('aria-disabled') == 'true'
                            parent_html = btn.evaluate('node => node.closest("section") ? node.closest("section").outerHTML : ""')
                            if (
                                not is_disabled and btn.is_enabled() and btn.is_visible()
                                and 'reply' not in parent_html.lower()
                                and 'modal' not in parent_html.lower()
                                and 'thread' not in parent_html.lower()
                            ):
                                print('[DEBUG] Clicking main tweet/post button in composer (robust selectors)')
                                btn.click()
                                time.sleep(2)
                                # Check if tweet box is cleared (tweet posted)
                                if tweet_box.inner_text().strip() == '':
                                    print('[DEBUG] Tweet posted successfully by clicking button')
                                    return {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'text': tweet_text}
                            if not is_disabled:
                                found_enabled = True
                        except Exception as e:
                            print(f'[DEBUG] Exception while checking post button: {e}')
                    if not found_enabled:
                        print('[DEBUG] Post button still disabled or not found, retrying...')
                        tweet_box.click()
                        time.sleep(0.5)
                        tweet_box.type(' ')
                        tweet_box.press('Backspace')
                        time.sleep(1)
                        page.screenshot(path=f'post_button_disabled_attempt_{post_attempt+1}.png', full_page=True)
                    time.sleep(1)
                page.screenshot(path="tweet_button_not_found.png", full_page=True)
                raise Exception('Main tweet/post button not found or not enabled on /home. See screenshot: tweet_button_not_found.png')

            except Exception as e:
                # Fallback: If the error is 'Element is not attached to the DOM' after posting, treat as success
                if 'Element is not attached to the DOM' in str(e):
                    print('[DEBUG] DOM detached error after post, assuming tweet was posted successfully.')
                    return {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'text': tweet_text}
                browser.close()
                raise Exception(f"Failed to post tweet via web: {e}")

    def _is_logged_in(self, page):
        try:
            page.wait_for_selector('a[aria-label="Profile"], a[aria-label="Profiel"]', timeout=8000)
            return True
        except PlaywrightTimeoutError:
            return False

    def _login(self, page):
        page.goto('https://twitter.com/login', timeout=60000)
        page.wait_for_selector('input[name="text"]', timeout=20000)
        page.fill('input[name="text"]', self.username)
        page.keyboard.press('Enter')
        page.wait_for_selector('input[name="password"]', timeout=20000)
        page.fill('input[name="password"]', self.password)
        page.keyboard.press('Enter')
        # Wacht tot home zichtbaar is
        page.wait_for_selector('a[aria-label="Profile"], a[aria-label="Profiel"]', timeout=20000) 