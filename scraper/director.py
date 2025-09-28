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

def get_director_albums(scraper, director_url):
    base_url = "https://www.masstamilan.dev"
    def get_movies_from_html(html):
        soup = BeautifulSoup(html, "html.parser")
        movies_divs = soup.find_all(class_="bots")
        movies = []
        for movie in movies_divs:
            for a in movie.find_all("a", href=True):
                if a.find_parent("nav") is None:
                    title = None
                    starring = None
                    music = None
                    director = None
                    h2 = a.find("h2")
                    if h2:
                        title = h2.text.strip()
                    p = a.find("p")
                    if p:
                        for b in p.find_all("b"):
                            label = b.text.strip(": ")
                            next_sibling = b.next_sibling
                            if label == "Starring":
                                starring = str(next_sibling).strip() if next_sibling else None
                            elif label == "Music":
                                music = str(next_sibling).strip() if next_sibling else None
                            elif label == "Director":
                                director = str(next_sibling).strip() if next_sibling else None
                    movies.append({
                        "title": title,
                        "starring": starring,
                        "music": music,
                        "director": director,
                        "url": a["href"]
                    })
        return movies

    # Get first page
    full_url = base_url + director_url if not director_url.startswith("http") else director_url
    html = scraper.get_html(full_url)
    all_movies = get_movies_from_html(html)
    soup = BeautifulSoup(html, "html.parser")
    nav = soup.find("nav", class_="pagy nav")
    page_urls = set()
    if nav:
        for a in nav.find_all("a", href=True):
            page_url = a["href"]
            if page_url.startswith("/"):
                page_urls.add(base_url + page_url)
            elif page_url.startswith("http"):
                page_urls.add(page_url)
    # Remove current page if present
    page_urls.discard(full_url)
    # Loop through all other pages
    for page_url in sorted(page_urls):
        html = scraper.get_html(page_url)
        all_movies.extend(get_movies_from_html(html))
    return all_movies
