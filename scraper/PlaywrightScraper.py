from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ui.utils import clear_screen


console = Console()


class PlaywrightScraper:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, args=[
            '--disable-blink-features=AutomationControlled'
        ])
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()
        self.page.set_viewport_size({"width": 1280, "height": 800})

    def _is_cloudflare_challenge(self):
        content = self.page.content().lower()
        markers = (
            "cf-chl-",
            "challenge-platform",
            "performance and security by cloudflare",
            'class="ray-id"',
        )
        return any(marker in content for marker in markers)

    def _wait_for_manual_challenge(self, timeout=180):
        instructions = Text()
        instructions.append("Website verification is required.\n\n", style="bold yellow")
        instructions.append("1. ", style="bold cyan")
        instructions.append(
            "Complete the CAPTCHA in the browser window.\n",
            style="white",
        )
        instructions.append("2. ", style="bold cyan")
        instructions.append(
            "Navigate and browse around the webpage if needed.\n",
            style="white",
        )
        instructions.append("3. ", style="bold cyan")
        instructions.append(
            "Click the page or a link to continue until the website loads.\n",
            style="white",
        )
        instructions.append("4. ", style="bold cyan")
        instructions.append(
            "Come back to this terminal and wait; downloading will resume automatically.\n\n",
            style="white",
        )
        instructions.append(
            f"Verification timeout: {timeout} seconds",
            style="bold bright_yellow",
        )
        console.print(
            Panel(
                instructions,
                title="[bold bright_magenta]Cloudflare Verification[/bold bright_magenta]",
                border_style="bright_cyan",
                padding=(1, 2),
            )
        )
        deadline = self.page.evaluate("Date.now()") + timeout * 1000
        while self._is_cloudflare_challenge():
            if self.page.evaluate("Date.now()") >= deadline:
                raise TimeoutError("Cloudflare verification was not completed in time.")
            self.page.wait_for_timeout(2000)

        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            # A challenge can finish without a full navigation.
            pass
        print("Cloudflare verification completed. Continuing...")
        clear_screen()

    def goto(self, url):
        self.page.goto(url, timeout=60000, wait_until="domcontentloaded")
        if self._is_cloudflare_challenge():
            self._wait_for_manual_challenge()

            # Some challenges redirect through a verification page before
            # returning to the requested URL. Reload it once automatically.
            if self.page.url != url:
                self.page.goto(url, timeout=60000, wait_until="domcontentloaded")
                if self._is_cloudflare_challenge():
                    raise RuntimeError(
                        "Cloudflare verification did not clear the requested page."
                    )
        return self.page

    def get_html(self, url):
        self.goto(url)
        return self.page.content()

    def get_cookies(self):
        return self.context.cookies()

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()
