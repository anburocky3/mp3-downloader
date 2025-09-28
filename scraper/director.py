from bs4 import BeautifulSoup

def get_music_directors(scraper, base_url):
    url = base_url
    html = scraper.get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    main_div = soup.find("div", class_="sb cen")
    if not main_div:
        # print(f"[bold red][ERROR][/bold red] No Music Directors data found")
        return None
    sections = main_div.find_all("section", class_="wid ctr")
    if not sections or len(sections) < 2:
        return None
    directors_section = sections[1]  # Get the second child
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

def get_director_albums(scraper, director_url, base_url):
    from urllib.parse import urljoin
    def parse_album_page(html):
        from bs4 import NavigableString
        soup = BeautifulSoup(html, "html.parser")
        albums = []
        bots_section = soup.find("section", class_="bots")
        if not bots_section:
            return []
        gw_div = bots_section.find("div")
        if not gw_div:
            return []
        gw_inner = gw_div.find("div", class_="gw")
        if not gw_inner:
            return []
        for a_i in gw_inner.find_all("div", class_="a-i"):
            a_tag = a_i.find("a")
            if not a_tag:
                continue
            album_url = a_tag.get("href")
            album_url = urljoin(base_url, album_url)
            mw0_div = a_tag.find("div", class_="mw0")
            album_title = None
            starring = None
            music = None
            director = None
            if mw0_div:
                h2 = mw0_div.find("h2")
                if h2:
                    album_title = h2.text.strip()
                p = mw0_div.find("p")
                if p:
                    for tag in p.contents:
                        if tag.name == "b":
                            label = tag.text.strip()
                            value = tag.next_sibling
                            # Sometimes value is a NavigableString, sometimes a Tag (e.g., <br>)
                            if isinstance(value, NavigableString):
                                value = value.strip()
                            elif value:
                                value = value.get_text(strip=True) if hasattr(value, 'get_text') else str(value).strip()
                            else:
                                value = ""
                            if label == "Starring:":
                                starring = value
                            elif label == "Music:":
                                music = value
                            elif label == "Director:":
                                director = value
            albums.append({
                "title": album_title,
                "url": album_url,
                "starring": starring,
                "music": music,
                "director": director
            })
        return albums
    # Helper to get all paginated URLs
    def get_all_pages(html, base_url, current_url):
        soup = BeautifulSoup(html, "html.parser")
        nav = soup.find("nav", class_="pagy nav")
        page_urls = set()
        if nav:
            for a in nav.find_all("a", href=True):
                href = a.get("href")
                if href and not a.has_attr("aria-disabled"):
                    full_url = urljoin(base_url, href)
                    page_urls.add(full_url)
        # Always include the current page
        page_urls.add(current_url)
        return list(page_urls)
    # Main logic
    full_url = base_url + director_url if not director_url.startswith("http") else director_url
    html = scraper.get_html(full_url)
    all_page_urls = get_all_pages(html, base_url, full_url)
    all_albums = []
    for page_url in sorted(set(all_page_urls)):
        page_html = scraper.get_html(page_url)
        page_albums = parse_album_page(page_html)
        all_albums.extend(page_albums)
    return all_albums
