from bs4 import BeautifulSoup
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.text import Text
from scraper.download import sanitize_filename

console = Console()

def get_trending_albums(scraper, base_url):
    url = base_url
    html = scraper.get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    main_div = soup.find("div", class_="sb cen")
    if not main_div:
        console.print("[bold red]Trending section not found. Debug HTML snippet below:[/bold red]")
        console.print(html[:1000])
        return []
    sections = main_div.find_all("section", class_="wid ctr")
    if not sections or len(sections) < 1:
        console.print("[bold red]Trending section not found.[/bold red]")
        return []
    trending_section = sections[0]
    ul = trending_section.find("ul")
    if not ul:
        console.print("[bold red]Trending albums list not found.[/bold red]")
        return []
    albums = []
    for li in ul.find_all("li"):
        a = li.find("a")
        if a:
            albums.append({
                "title": a.text.strip(),
                "url": a.get("href")
            })
    return albums

def download_album_songs(scraper, album_url, album_name, output_dir=None, base_url=None):
    import os
    if base_url is None:
        base_url = "https://www.masstamilan.dev"
    full_url = base_url + album_url if not album_url.startswith("http") else album_url
    try:
        scraper.goto(full_url)
        scraper.page.wait_for_selector("tbody", timeout=10000)
        html = scraper.page.content()
    except Exception as e:
        console.print(f"[bold red]Error loading album page: {e}[/bold red]")
        html = scraper.page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Extract year from the album page
    year_tag = soup.find("a", href=True, title=lambda t: t and t.startswith("See all movies released in "))
    album_year = None
    if year_tag:
        album_year = year_tag.text.strip()
    if album_year:
        album_dir_name = f"{album_name} - ({album_year})"
    else:
        album_dir_name = album_name
    album_dir_name = sanitize_filename(album_dir_name)
    if output_dir:
        album_dir = os.path.join(output_dir, album_dir_name)
    else:
        album_dir = os.path.join("downloaded", album_dir_name)
    os.makedirs(album_dir, exist_ok=True)

    song_links = []
    for tr in soup.find_all("tr", itemprop="itemListElement"):
        # Track name
        name_tag = tr.find("span", itemprop="name")
        song_name = name_tag.get_text(strip=True) if name_tag else "Unknown"
        song_name = sanitize_filename(song_name)
        # Download links
        dlinks = tr.find_all("a", class_="dlink")
        if dlinks:
            best_link = dlinks[-1]  # Last link (highest quality)
            song_url = best_link.get("href")
            song_links.append({
                "title": song_name,
                "url": song_url
            })
    if not song_links:
        console.print(f"[bold yellow]No song download links found in album HTML.[/bold yellow]")
        return {"downloaded": [], "failed": [{"title": "Album", "reason": "No song download links found"}], "path": album_dir}
    downloaded_files = []
    failed_files = []
    for idx, song in enumerate(song_links, 1):
        song_url = song["url"]
        if not song_url.startswith("http"):
            song_url = base_url + song_url
        local_filename = os.path.join(album_dir, song["title"] + ".mp3")
        download = None
        try:
            with scraper.page.expect_download() as download_info:
                scraper.page.evaluate(f'''
                    var a = document.createElement('a');
                    a.href = {json.dumps(song_url)};
                    a.download = '';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                ''')
            download = download_info.value
            download.save_as(local_filename)
            downloaded_files.append(local_filename)
            console.print(
                f"[bold green]Downloaded:[/bold green] [white]{song['title']}.mp3[/white] "
                f"[dim]→ {local_filename}[/dim]"
            )
        except Exception as e:
            reason = str(e).strip() or e.__class__.__name__
            if download is not None:
                download_failure = download.failure()
                if download_failure:
                    reason = download_failure
            if "canceled" in reason.lower():
                reason = (
                    "The server or browser canceled the download "
                    "(the link may require verification or be unavailable)"
                )
            failed_files.append({"title": song["title"], "reason": reason})
            console.print(
                f"[bold red]Failed:[/bold red] [white]{song['title']}[/white] "
                f"[dim]— {reason}[/dim]"
            )
    # Summary panel
    summary_text = Text()
    summary_text.append("\nAlbum saved to: ", style="bold cyan")
    summary_text.append(f"{album_dir} \n", style="bold yellow")
    summary_text.append("Saved to: ", style="bold cyan")
    summary_text.append(f"{os.path.abspath(album_dir)}\n", style="bold yellow")
    summary_text.append("Downloaded: ", style="bold magenta")
    summary_text.append(f"{len(downloaded_files)}\n", style="bold green")
    summary_text.append("Failed: ", style="bold magenta")
    summary_text.append(f"{len(failed_files)}\n", style="bold red" if failed_files else "bold green")
    if failed_files:
        summary_text.append("\nFailure details:\n", style="bold red")
        for failure in failed_files:
            summary_text.append(
                f"• {failure['title']}: {failure['reason']}\n",
                style="red",
            )
    summary_text.append(f"Author: Anbuselvan Rocky", style="bold blue")
    console.print(Panel(summary_text, title=f"Download Summary for - {album_name} ({album_year})", box=box.ROUNDED, border_style="bright_magenta"))
    return {"downloaded": downloaded_files, "failed": failed_files, "path": album_dir}
