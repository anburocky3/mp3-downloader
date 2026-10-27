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
        soup = BeautifulSoup(html, "html.parser")
        albums = []

        for a_i in soup.select("div.a-i"):
            a_tag = a_i.find("a")
            if not a_tag:
                continue

            info = a_tag.select_one("div.mw0")
            if not info:
                continue

            title_tag = info.find("h2")
            details = {
                "Starring:": "",
                "Music:": "",
                "Director:": "",
            }
            details_tag = info.find("p")
            if details_tag:
                for label_tag in details_tag.find_all("b"):
                    label = label_tag.get_text(strip=True)
                    if label not in details:
                        continue
                    value_parts = []
                    for sibling in label_tag.next_siblings:
                        if getattr(sibling, "name", None) == "br":
                            break
                        text = sibling.get_text(" ", strip=True) if hasattr(sibling, "get_text") else str(sibling).strip()
                        if text:
                            value_parts.append(text)
                    details[label] = " ".join(value_parts)

            albums.append({
                "title": title_tag.get_text(strip=True) if title_tag else "",
                "url": urljoin(base_url, a_tag.get("href", "")),
                "starring": details["Starring:"],
                "music": details["Music:"],
                "director": details["Director:"],
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
