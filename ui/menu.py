from rich import box
from rich.console import Console
from rich.table import Table
import readchar
from time import sleep

from scraper.album import get_trending_albums, download_album_songs
from scraper.director import get_music_directors, get_director_albums
import sys
from scraper.download import sanitize_filename

from ui.utils import clear_screen

console = Console()
languages = [
    ("Tamil", "https://www.masstamilan.dev", "masstamilan.dev"),
    ("Hindi", "https://mp3bhai.com", "mp3bhai.com"),
    ("Telugu", "https://masstelugu.com", "masstelugu.com"),
    ("Malayalam", "https://mp3chetta.com", "mp3chetta.com"),
]

def select_ui_option(scraper, base_url):
    tamil_options = [
        ("🎵  Trending Songs", "trending"),
        ("🎤  Songs by Music Directors", "directors"),
    ]
    while True:
        console.print("[bold yellow]Please wait...[/bold yellow]")
        clear_screen()
        table = Table(
            title="[bold magenta]How do you want to download?[/bold magenta]",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            padding=(1, 2),
            title_justify="center"
        )
        table.add_column("No.", style="bold cyan", justify="center", width=6)
        table.add_column("Option", style="bold yellow", justify="left", width=40)
        for idx, (opt, _) in enumerate(tamil_options, 1):
            table.add_row(f"[bold green]{idx}[/bold green]", f"{opt}")
        table.add_row("[bold red]0[/bold red]", "[bold red]Exit[/bold red]")
        console.clear()
        console.print(table)
        console.print("[bold green]Enter the number of your choice (0 to exit, Esc to go back):[/bold green] ", end="")
        key = readchar.readkey()
        if key == readchar.key.ESC:
            return None
        if key == "0":
            console.print("[bold magenta]Good bye![/bold magenta]")
            sys.exit(0)
        if key in map(str, range(1, len(tamil_options)+1)):
            selected = tamil_options[int(key)-1][1]
            console.print(f"\n[bold blue]You selected: {tamil_options[int(key)-1][0]}[/bold blue], please wait...\n")
            clear_screen()
            console.print("[bold yellow]Please wait...[/bold yellow]")
            if selected == "trending":
                console.print("[bold yellow]Please wait while we fetch trending albums...[/bold yellow]")
                clear_screen()
                albums = get_trending_albums(scraper, base_url)
                if albums:
                    table = Table(
                        title="[bold magenta]:fire: Trending Albums :fire:[/bold magenta]",
                        show_header=True,
                        header_style="bold magenta",
                        box=box.ROUNDED,
                        padding=(1, 2),
                        title_justify="center"
                    )
                    table.add_column("No.", style="bold cyan", justify="center", width=6)
                    table.add_column(":cd:  Album", style="bold yellow", justify="left", width=40)
                    table.add_column(":link: URL", style="bold green", justify="left", width=40)
                    for idx, album in enumerate(albums, 1):
                        table.add_row(f"[bold green]{idx}[/bold green]", f"[bold yellow]{album['title']}[/bold yellow]", f"[dim]{album['url']}[/dim]")
                    console.print(table)
                    console.print("[bold green]Enter album number to download all songs or Esc to go back:[/bold green] \n", end="")
                    key2 = readchar.readkey()
                    if key2 == readchar.key.ESC:
                        return None
                    if key2 in map(str, range(1, len(albums)+1)):
                        album = albums[int(key2)-1]
                        download_album_songs(scraper, album["url"], album["title"], base_url=base_url)
                else:
                    console.print("[bold red]No trending albums found.[/bold red]")
            elif selected == "directors":
                console.print("[bold yellow]Please wait while we fetch music directors...[/bold yellow]")
                clear_screen()
                directors = get_music_directors(scraper, base_url)
                if directors is None:
                    console.print("[bold red]Director data not available.[/bold red]")
                    return None
                if directors:
                    table = Table(
                        title="[bold magenta]:star: Music Directors :star:[/bold magenta]",
                        show_header=True,
                        header_style="bold magenta",
                        box=box.ROUNDED,
                        padding=(1, 2),
                        title_justify="center"
                    )
                    table.add_column("No.", style="bold cyan", justify="center", width=6)
                    table.add_column(":man_artist: Director", style="bold yellow", justify="left", width=40)
                    table.add_column(":link: URL", style="bold green", justify="left", width=40)
                    for idx, director in enumerate(directors, 1):
                        table.add_row(f"[bold green]{idx}[/bold green]", f"[bold yellow]{director['name']}[/bold yellow]", f"[dim]{director['url']}[/dim]")
                    console.print(table)
                    console.print("[bold green]Enter director number to view albums or Esc to go back:[/bold green] ", end="")
                    try:
                        input_str = console.input("[bold green]Your choice: [/bold green]")
                    except KeyboardInterrupt:
                        console.print("\n[bold magenta]Good bye![/bold magenta]")
                        sys.exit(0)
                    if input_str.lower() == 'esc':
                        return None
                    if input_str.isdigit() and 1 <= int(input_str) <= len(directors):
                        key2 = input_str
                        console.print("[italic blue]Please wait while we fetch all the records... (May take time...)[/italic blue]")
                        director = directors[int(key2)-1]
                        albums = get_director_albums(scraper, director["url"], base_url=base_url)
                        if albums:
                            clear_screen()
                            table = Table(
                                title=f"[bold magenta]:musical_note: Albums by {director['name']} :musical_note:[/bold magenta]",
                                show_header=True,
                                header_style="bold magenta",
                                box=box.ROUNDED,
                                padding=(1, 2),
                                title_justify="center"
                            )
                            table.add_column("No.", style="bold cyan", justify="center", width=6)
                            table.add_column(":cd: Album", style="bold yellow", justify="left", width=40)
                            table.add_column(":link: URL", style="bold green", justify="left", width=40)
                            for idx, album in enumerate(albums, 1):
                                album_title = f"[bold yellow][b][u]{album['title']}[/u][/b][/bold yellow]"
                                album_details = f"[dim white]:busts_in_silhouette: Starring: {album['starring'] or ''}\n:musical_score: Music: {album['music'] or ''}\n:clapper: Director: {album['director'] or ''}[/dim white]"
                                album_info = f"{album_title}\n{album_details}"
                                table.add_row(f"[bold green]{idx}[/bold green]", album_info, f"[dim]{album['url']}[/dim]")
                            console.print(table)
                            console.print("[bold green]Enter album number(s) separated by comma to download, type 'all' to download all albums, or Esc to go back:[/bold green]")
                            try:
                                input_str = console.input("[bold green]Your choice: [/bold green]")
                            except KeyboardInterrupt:
                                console.print("\n[bold magenta]Good bye![/bold magenta]")
                                sys.exit(0)
                            if input_str.lower() == 'esc':
                                console.print("[bold magenta]Good bye![/bold magenta]")
                                return None
                            if input_str.lower() == 'all':
                                selected_indices = list(range(1, len(albums)+1))
                            else:
                                selected_indices = []
                                for part in input_str.split(','):
                                    part = part.strip()
                                    if part.isdigit():
                                        idx = int(part)
                                        if 1 <= idx <= len(albums):
                                            selected_indices.append(idx)
                            import os
                            director_folder = os.path.join('downloaded', sanitize_filename(director['name']))
                            os.makedirs(director_folder, exist_ok=True)
                            for idx in selected_indices:
                                album = albums[idx-1]
                                safe_album_title = sanitize_filename(album["title"])
                                download_album_songs(scraper, album["url"], safe_album_title, output_dir=director_folder, base_url=base_url)
                        else:
                            console.print("[bold red]No albums found for this director.[/bold red]")
                else:
                    console.print("[bold red]No directors found.[/bold red]")
            return selected
        else:
            console.print("\n[bold red]Invalid selection. Please try again.[/bold red]")


def select_language(scraper):
    while True:
        table = Table(title="Select Music Language",
                      show_header=True,
                      header_style="bold magenta",
                      box=box.ROUNDED,
                      padding=(1, 2),
                      title_justify="center")
        table.add_column("No.", style="bold cyan", justify="center", width=6)
        table.add_column("Language", style="bold yellow", width=40)
        table.add_column("Platforms", width=40)
        for idx, (lang, url, name) in enumerate(languages, 1):
            table.add_row(str(idx), lang, name)
        table.add_row("[bold red]0[/bold red]", "[bold red]Exit[/bold red]", "")
        console.clear()
        console.print(table)
        console.print("[bold green]Enter the number of your choice (0 to exit, Esc to go back):[/bold green] ", end="")
        key = readchar.readkey()
        if key == readchar.key.ESC:
            console.print("\n[bold magenta]Going back...[/bold magenta]")
            break
        if key == "0":
            console.print("[bold magenta]Good bye![/bold magenta]")
            sys.exit(0)
        if key in map(str, range(1, len(languages)+1)):
            lang, url, name = languages[int(key)-1]
            console.print(f"\n[bold blue] You selected {lang}. Opening platform: {url}[/bold blue]\n")
            if lang == "Tamil" or lang == "Telugu" or lang == "Hindi" or lang == "Malayalam":
                select_ui_option(scraper, url)
                break
            else:
                import webbrowser
                webbrowser.open(url)
                break
        else:
            console.print("\n[bold red]Invalid selection. Please try again.[/bold red]")
