from bs4 import BeautifulSoup
from .PlaywrightScraper import PlaywrightScraper

def get_music_directors(scraper):
    url = "https://www.masstamilan.dev/"
    html = scraper.get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    main_div = soup.find("div", class_="sb cen")
    if not main_div:
        print("[bold red]Directors section not found.[/bold red]")
        return []
    sections = main_div.find_all("section", class_="wid ctr")
    if len(sections) < 2:
        print("[bold red]Directors section not found.[/bold red]")
        return []
    directors_section = sections[1]
    ul = directors_section.find("ul")
    if not ul:
        print("[bold red]Directors list not found.[/bold red]")
        return []
    directors = []
    for li in ul.find_all("li"):
        a = li.find("a")
        if a:
            directors.append({
                "name": a.text.strip(),
                "url": a.get("href")
            })
    return directors

def get_director_songs(scraper, director_url):
    base_url = "https://www.masstamilan.dev"
    full_url = base_url + director_url if not director_url.startswith("http") else director_url
    html = scraper.get_html(full_url)
    soup = BeautifulSoup(html, "html.parser")
    movie_links = soup.find_all("a", href=True)
    movies = []
    for a in movie_links:
        href = a["href"]
        if href.startswith("/") and "songs" in href:
            movies.append({
                "title": a.text.strip(),
                "url": href
            })
    return movies

