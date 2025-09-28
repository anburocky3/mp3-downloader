import os

def download_song(scraper, song_url, song_title, album_name=None):
    base_url = "https://www.masstamilan.dev"
    full_url = base_url + song_url if not song_url.startswith("http") else song_url
    local_filename = song_title.replace(" ", "_") + ".mp3"
    if album_name:
        album_dir = os.path.join("downloaded", album_name.replace(" ", "_"))
        os.makedirs(album_dir, exist_ok=True)
        local_filename = os.path.join(album_dir, local_filename)
    with scraper.page.expect_download() as download_info:
        scraper.page.goto(full_url)
    download = download_info.value
    download.save_as(local_filename)
    print(f"[bold green]Downloaded: {local_filename}[/bold green]")

