from rich.console import Console
from rich.table import Table
import readchar
from scraper.album import get_trending_albums, download_album_songs
from scraper.director import get_music_directors, get_director_songs
from scraper.download import download_song

console = Console()
languages = [
    ("Tamil", "https://www.masstamilan.dev/"),
    ("Hindi", "https://mp3bhai.com/"),
    ("Telugu", "https://masstelugu.com/"),
    ("Malayalam", "https://mp3chetta.com/"),
]

def select_tamil_option(scraper):
    tamil_options = [
        ("Trending Songs", "trending"),
        ("Songs by Music Directors", "directors"),
    ]
    while True:
        table = Table(title="How do you want to download?", show_header=True, header_style="bold magenta")
        table.add_column("No.", style="bold cyan")
        table.add_column("Option", style="bold yellow")
        for idx, (opt, _) in enumerate(tamil_options, 1):
            table.add_row(str(idx), opt)
        console.clear()
        console.print(table)
        console.print("[bold green]Enter the number of your choice:[/bold green] ", end="")
        key = readchar.readkey()
        if key == readchar.key.ESC:
            return None
        if key in map(str, range(1, len(tamil_options)+1)):
            selected = tamil_options[int(key)-1][1]
            console.print(f"\n[bold blue]You selected: {tamil_options[int(key)-1][0]}[/bold blue], please wait...")
            if selected == "trending":
                albums = get_trending_albums(scraper)
                if albums:
                    table = Table(title="Trending Albums", show_header=True, header_style="bold magenta")
                    table.add_column("No.", style="bold cyan")
                    table.add_column("Album", style="bold yellow")
                    table.add_column("URL", style="bold green")
                    for idx, album in enumerate(albums, 1):
                        table.add_row(str(idx), album["title"], album["url"])
                    console.print(table)
                    console.print("[bold green]Enter album number to download all songs or Esc to go back:[/bold green] \n", end="")
                    key2 = readchar.readkey()
                    if key2 == readchar.key.ESC:
                        return None
                    if key2 in map(str, range(1, len(albums)+1)):
                        album = albums[int(key2)-1]
                        download_album_songs(scraper, album["url"], album["title"])
                else:
                    console.print("[bold red]No trending albums found.[/bold red]")
            elif selected == "directors":
                directors = get_music_directors(scraper)
                if directors:
                    table = Table(title="Music Directors", show_header=True, header_style="bold magenta")
                    table.add_column("No.", style="bold cyan")
                    table.add_column("Director", style="bold yellow")
                    table.add_column("URL", style="bold green")
                    for idx, director in enumerate(directors, 1):
                        table.add_row(str(idx), director["name"], director["url"])
                    console.print(table)
                    console.print("[bold green]Enter director number to view albums or Esc to go back:[/bold green] ", end="")
                    key2 = readchar.readkey()
                    if key2 == readchar.key.ESC:
                        return None
                    if key2 in map(str, range(1, len(directors)+1)):
                        director = directors[int(key2)-1]
                        albums = get_director_songs(scraper, director["url"])
                        if albums:
                            table = Table(title=f"Albums by {director['name']}", show_header=True, header_style="bold magenta")
                            table.add_column("No.", style="bold cyan")
                            table.add_column("Album", style="bold yellow")
                            table.add_column("URL", style="bold green")
                            for idx, album in enumerate(albums, 1):
                                table.add_row(str(idx), album["title"], album["url"])
                            console.print(table)
                            console.print("[bold green]Enter album number to download all songs or Esc to go back:[/bold green] ", end="")
                            key3 = readchar.readkey()
                            if key3 == readchar.key.ESC:
                                return None
                            if key3 in map(str, range(1, len(albums)+1)):
                                album = albums[int(key3)-1]
                                download_album_songs(scraper, album["url"], album["title"])
                        else:
                            console.print("[bold red]No albums found for this director.[/bold red]")
                else:
                    console.print("[bold red]No directors found.[/bold red]")
            return selected
        else:
            console.print("\n[bold red]Invalid selection. Please try again.[/bold red]")

def select_language(scraper):
    while True:
        table = Table(title="Select Music Language", show_header=True, header_style="bold magenta")
        table.add_column("No.", style="bold cyan")
        table.add_column("Language", style="bold yellow")
        for idx, (lang, _) in enumerate(languages, 1):
            table.add_row(str(idx), lang)
        console.clear()
        console.print(table)
        console.print("[bold green]Enter the number of your choice:[/bold green] ", end="")
        key = readchar.readkey()
        if key == readchar.key.ESC:
            console.print("\n[bold red]Exiting...[/bold red]")
            break
        if key in map(str, range(1, len(languages)+1)):
            lang, url = languages[int(key)-1]
            console.print(f"\n[bold blue] You selected {lang}. Opening platform: {url}[/bold blue]\n")
            if lang == "Tamil":
                select_tamil_option(scraper)
                break
            else:
                import webbrowser
                webbrowser.open(url)
                break
        else:
            console.print("\n[bold red]Invalid selection. Please try again.[/bold red]")
