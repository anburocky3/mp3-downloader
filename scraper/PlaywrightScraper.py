import time
from playwright.sync_api import sync_playwright

class PlaywrightScraper:
    def __init__(self):
        self.playwright = sync_playwright().start()
        # Run browser in headless mode to keep terminal in focus
        self.browser = self.playwright.chromium.launch(headless=True, args=[
            '--disable-blink-features=AutomationControlled'
        ])
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()
        self.page.set_viewport_size({"width": 1280, "height": 800})

    def get_html(self, url):
        self.page.goto(url, timeout=60000)
        try:
            self.page.wait_for_selector('div.sb.cen', timeout=20000)
            time.sleep(3)
        except Exception as e:
            print(f"[DEBUG] .sb.cen not found: {e}")
        html = self.page.content()
        # print('[DEBUG] HTML after navigation:', html[:1000])
        return html

    def get_cookies(self):
        return self.context.cookies()

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()
