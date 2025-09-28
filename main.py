from scraper.PlaywrightScraper import PlaywrightScraper
from ui.menu import select_language

def print_banner():
    print("╔════════════════════════════════════════╗")
    print("║  🎵  𝙈𝙋𝟯 𝘿𝙤𝙬𝙣𝙡𝙤𝙖𝙙𝙚𝙧 in single click  🎵  ║")
    print("╚════════════════════════════════════════╝\n")

def main():
    print_banner()
    scraper = PlaywrightScraper()
    try:
        select_language(scraper)
    finally:
        scraper.close()

if __name__ == '__main__':
    main()

