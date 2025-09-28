from bs4 import BeautifulSoup
from .PlaywrightScraper import PlaywrightScraper

def get_music_directors(scraper, base_url):
    url = base_url + "/music/"
    html = scraper.get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    main_div = soup.find("div", class_="sb cen")
    if not main_div:
        print(f"[bold red][ERROR][/bold red] No Music Directors data found")
        return None
    sections = main_div.find_all("section", class_="wid ctr")
    if not sections or len(sections) < 1:
        return None
    directors_section = sections[0]
    ul = directors_section.find("ul")
    if not ul:
        return None
    directors = []
    for li in ul.find_all("li"):
        a = li.find("a")
        if a:
            directors.append({
                "name": a.text.strip(),
                "url": a.get("href")
            })
    return directors

def get_director_albums(scraper, director_url, base_url=None):
    if base_url is None:
        base_url = "https://www.masstamilan.dev"
    full_url = base_url + director_url if not director_url.startswith("http") else director_url
    html = scraper.get_html(full_url)
    soup = BeautifulSoup(html, "html.parser")
    def get_movies_from_html(html):
        soup = BeautifulSoup(html, "html.parser")
        main_div = soup.find("div", class_="sb cen")
        if not main_div:
            return []
        sections = main_div.find_all("section", class_="wid ctr")
        if not sections or len(sections) < 1:
            return []
        albums = []
        for section in sections:
            ul = section.find("ul")
            if not ul:
                continue
            for li in ul.find_all("li"):
                a = li.find("a")
                if a:
                    album_title = a.text.strip()
                    album_url = a.get("href")
                    starring = None
                    music = None
                    director = None
                    info_div = li.find("div", class_="mw0")
                    if info_div:
                        p = info_div.find("p")
                        if p:
                            lines = p.decode_contents().split("<br>")
                            for line in lines:
                                if "Starring:" in line:
                                    starring = line.split("Starring:")[-1].strip()
                                if "Music:" in line:
                                    music = line.split("Music:")[-1].strip()
                                if "Director:" in line:
                                    director = line.split("Director:")[-1].strip()
                    albums.append({
                        "title": album_title,
                        "url": album_url,
                        "starring": starring,
                        "music": music,
                        "director": director
                    })
        return albums
    return get_movies_from_html(html)
