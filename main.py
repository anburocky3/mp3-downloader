from rich.console import Console
from scraper.PlaywrightScraper import PlaywrightScraper
from ui.menu import select_language
from ui.utils import clear_screen

console = Console()

def print_banner():
    clear_screen()
    banner_lines = [
        ("#####  ######     #    ######  ######  ####### ######  ", "bold yellow"),
        ("#     # #     #   # #   #     # #     # #       #     # ", "bold bright_yellow"),
        ("#       #     #  #   #  #     # #     # #       #     # ", "bold orange3"),
        ("#  #### ######  #     # ######  ######  #####   ######  ", "bold magenta"),
        ("#     # #   #   ####### #     # #     # #       #   #   ", "bold blue"),
        ("#     # #    #  #     # #     # #     # #       #    #  ", "bold cyan"),
        ("#####  #     # #     # ######  ######  ####### #     # ", "bold green"),
    ]
    for line, style in banner_lines:
        console.print(line, style=style)
    console.print("[bold magenta]╔════════════════════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold white]║  🎺  1000+ mp3 in single click  | 😎  Anbuselvan Rocky   ║[/bold white]")
    console.print("[bold magenta]╚════════════════════════════════════════════════════════╝\n[/bold magenta]")


def main():
    print_banner()
    scraper = PlaywrightScraper()
    try:
        select_language(scraper)
    finally:
        scraper.close()

if __name__ == '__main__':
    main()
