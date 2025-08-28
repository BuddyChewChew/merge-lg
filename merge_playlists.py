import requests
from urllib.parse import urlparse
import os

def download_playlist(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None

def extract_streams(playlist_content):
    if not playlist_content:
        return set()
    
    # Split into lines and filter out empty lines and comments
    lines = [line.strip() for line in playlist_content.split('\n') if line.strip() and not line.startswith('#')]
    
    # Group into EXTINF and URL pairs
    streams = set()
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith('EXTINF'):
            if i + 1 < len(lines):
                streams.add((lines[i], lines[i+1]))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return streams

def merge_playlists(urls):
    all_streams = set()
    
    for url in urls:
        print(f"Processing {url}...")
        content = download_playlist(url)
        if content:
            streams = extract_streams(content)
            all_streams.update(streams)
            print(f"  - Found {len(streams)} streams")
    
    return all_streams

def save_merged_playlist(streams, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for extinf, url in sorted(streams, key=lambda x: x[0].lower()):
            f.write(f"{extinf}\n{url}\n")

def main():
    playlist_urls = [
        "https://www.apsattv.com/uslg.m3u",
        "https://www.apsattv.com/calg.m3u",
        "https://www.apsattv.com/nzlg.m3u"
    ]
    
    output_file = "merged_playlist.m3u"
    
    print("Starting to merge playlists...")
    merged_streams = merge_playlists(playlist_urls)
    
    print(f"\nTotal unique streams found: {len(merged_streams)}")
    print(f"Saving to {output_file}...")
    save_merged_playlist(merged_streams, output_file)
    print("Done!")

if __name__ == "__main__":
    main()
